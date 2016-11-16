from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import logging
from ..forms.datasets import DatasetForm, DataSelectForm
from ..forms.identifier import IdentifierForm
from ..models import Project, Specimen, Process, Dataset, Data, Identifier
from ids.utils import (get_portal_api_client,
                       get_process_type_keys,
                       get_dataset_fields)
from requests import HTTPError
import urllib

from ezid.ezid import ezidClient
from ezid.identifier_creator import identifierBuilder
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def _add_identifier_to_dataset(dataset, identifier):
    if (dataset != None):
        identifier.add_to_dataset(dataset)
        identifier.save()
        dataset.add_identifier(identifier)
        dataset.save()
    return dataset


# Update alternateIdentifier field as the shoadow ARK identifier
def update_alternateIdentifier(essential_meta, ark):
    alternateIdentifiers = []
    alternateIdentifier = {}
    alternateIdentifier['alternateIdentifierType'] = 'ARK'
    alternateIdentifier['text'] = ark
    alternateIdentifiers.append(alternateIdentifier)

    essential_meta['alternateIdentifiers'] = alternateIdentifiers
    # print json.dumps(essential_meta, indent = 2)
    return essential_meta


def meta_for_ark(dataset):
    project = dataset.project

    metadata = {}
    metadata['erc.who'] = project.value.get('creator', None)
    metadata['erc.what'] = dataset.title
    metadata['erc.when'] = datetime.date.today().strftime("%B %d, %Y")

    return metadata


def meta_for_doi(dataset, form_data=None):
    """ constructing json for build xml object """
    project = dataset.project

    dates = []
    formats = []
    versions = []
    rights = []

    if form_data:
        date = form_data.get('date', None)
        format = form_data.get('format', None)
        version = form_data.get('version', None)
        right = form_data.get('right', None)

    metadata = {}
    creators = []
    creator = {}
    creator['creatorName'] = {}
    creator['creatorName']['text'] = project.value.get('creator', None)
    creators.append(creator)

    titles = []
    title = {}
    title['xml:lang'] = "en-us"
    title['text'] = dataset.title
    titles.append(title)

    subjects = []
    subject = {}
    subject['xml:lang'] = "en-us"
    subject['text'] = project.value.get('investigation_type', '(:unas)')
    subjects.append(subject)

    resourceType = {}
    resourceType['resourceTypeGeneral'] = "Dataset"
    resourceType['text'] = dataset.value.get('name', '(:unas)')

    descriptions = []
    description = {}
    description['xml:lang'] = "en-us"
    description['descriptionType'] = "Abstract"
    description['text'] = dataset.value.get('description', '(:unas)')
    descriptions.append(description)

    metadata['creators'] = creators
    metadata['titles'] = titles
    metadata['subjects'] = subjects
    metadata['descriptions'] = descriptions

    # TODO: Add dates, sizes, formats, version, rghtsList, description, if necessary
    # print json.dumps(metadata, indent = 2)
    return metadata


@login_required
@require_http_methods(['GET', 'POST'])
def create(request, dataset_uuid):
    """Create a new dataset"""

    identifier_fields = [{'form_field': True,
                          'id': 'Date',
                          'label': 'Date',
                          'required': False},
                         {'form_field': True,
                          'id': 'Format',
                          'label': 'Format',
                          'required': False},
                         {'form_field': True,
                          'id': 'Version',
                          'label': 'Version',
                          'required': False},
                         {'form_field': True,
                          'id': 'Rights',
                          'label': 'Rights',
                          'required': False},
                         {'form_field': True,
                          'id': 'creatorName',
                          'label': 'Creator Name',
                          'required': False},
                         {'form_field': True,
                          'id': 'description',
                          'label': 'Description',
                          'required': False},
                         {'form_field': True,
                          'id': 'subject',
                          'label': 'Subject',
                          'required': False},
                         {'form_field': True,
                          'id': 'title',
                          'label': 'Title',
                          'required': False},
                         ]

    api_client = request.user.agave_oauth.api_client
    dataset = Dataset(api_client=api_client, uuid=dataset_uuid)
    essential = meta_for_doi(dataset)

    initial_data =  {'creatorName': essential['creators'][0]['creatorName']['text'],
                     'description': essential['descriptions'][0]['text'],
                     'subject': essential['subjects'][0]['text'],
                     'title': essential['titles'][0]['text']}

    context = dict()

    #######
    # GET #
    #######
    if request.method == 'GET':
        context['form_identifier_create'] = IdentifierForm(fields=identifier_fields, initial=initial_data)

        return render(request, 'ids_projects/identifier/create.html', context)

    ########
    # POST #
    ########
    if request.method == 'POST':
        builder = identifierBuilder()
        builder.buildXML(essential)
        xmlObject = builder.getXML()

        # requesting doi
        client = ezidClient('apitest', 'apitest')
        metadata = {}
        metadata["datacite"] = ET.tostring(xmlObject, encoding = "UTF-8", method = "xml")
        response = client.Mint('doi:10.5072/FK2', metadata)
        if "success" in response.keys():
            res = response['success']
            doi = res.split('|')[0].strip()
            ark = res.split('|')[1].strip()

            # update generated ARK as alternative identifier
            essential_new = update_alternateIdentifier(essential, ark)
            builder.setAlternateIdentifiers(essential_new)
            xmlObject = builder.getXML()
            metadata["datacite"] = ET.tostring(xmlObject, encoding = "UTF-8", method = "xml")
            response = client.Update(doi, metadata)

            # save identifier objects
            identifier = Identifier(api_client=api_client, type='doi', uid=doi, dataset=dataset)
            identifier.save()
            dataset = _add_identifier_to_dataset(dataset, identifier)

            # NOTES:
            # It seems due to network delay, results are not printed immediately.
            # However, the metadata were successfully updated in agave
            # for elem in dataset.identifiers:
            #     print elem.title, elem.uid

        else:
            logger.error("Failed to mint a DOI identifier!")
            messages.warning(request, "Error in requesting DOI!")
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))


        return HttpResponseRedirect(reverse('ids_projects:dataset-view', kwargs={'dataset_uuid': dataset.uuid}))


@require_http_methods(['GET'])
def view(request, identifier_uuid):
    """View a specific identifier"""
    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    try:
        identifier = Identifier(api_client=api_client, uuid=identifier_uuid)
    except Exception as e:
        exception_msg = 'Unable to load process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        uid = identifier.uid
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)

    url = "http://ezid.cdlib.org/id/" + uid

    return HttpResponseRedirect(url)
