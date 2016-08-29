from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import logging
from ..forms.datasets import DatasetForm, DataSelectForm
from ..models import Project, Specimen, Process, Dataset, Data
from ids.utils import (get_portal_api_client,
                       get_process_type_keys,
                       get_dataset_fields)
from requests import HTTPError
import urllib

from ezid.ezid import ezidClient
from ezid.identifier_creator import identifierBuilder
import xml.etree.ElementTree as ET
import json
import sys
import datetime

logger = logging.getLogger(__name__)


@require_http_methods(['GET'])
def list_public(request):
    """List all public datasets in a project"""
    api_client = get_portal_api_client()

    try:
        public_datasets = Dataset.list(api_client=api_client)
    except Exception as e:
        exception_msg = 'Unable to load datasets. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    context = { 'public_datasets': public_datasets }

    return render(request, 'ids_projects/datasets/index.html', context)


@login_required
@require_http_methods(['GET'])
def list_private(request):
    """List all private datasets in a project"""
    api_client = request.user.agave_oauth.api_client
    project_uuid = request.GET.get('project_uuid', None)

    if not project_uuid:
        messages.warning(request, 'Missing project UUID, cannot find datasets.')
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        project = Project(api_client=api_client, uuid=project_uuid)
        private_datasets = project.datasets

    except Exception as e:
        exception_msg = 'Unable to load datasets. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    context = { 'project': project,
                'private_datasets': private_datasets
              }

    return render(request, 'ids_projects/processes/index.html', context)


@require_http_methods(['GET'])
def view(request, dataset_uuid):
    """View a specific dataset"""
    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    try:
        dataset = Dataset(api_client=api_client, uuid=dataset_uuid)
        project = dataset.project
        data = dataset.data
    except Exception as e:
        exception_msg = 'Unable to load process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        process_types = get_process_type_keys(project)
        dataset_fields = get_dataset_fields(project)
        dataset.set_fields(dataset_fields)
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)

    context = { 'project': project,
                'dataset': dataset,
                'datas': data,
                'process_types': process_types }

    return render(request, 'ids_projects/datasets/detail.html', context)


@require_http_methods(['GET', 'POST'])
@login_required
def select_data(request, dataset_uuid):
    """List data to add to dataset."""
    api_client = request.user.agave_oauth.api_client

    try:
        dataset = Dataset(api_client=api_client, uuid=dataset_uuid)
        project = dataset.project
        dataset_data = [x.uuid for x in dataset.data]
        project_data = [x.uuid for x in project.data]
    except Exception as e:
        exception_msg = 'Unable to load process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        process_types = get_process_type_keys(project)
        dataset_fields = get_dataset_fields(project)
        dataset.set_fields(dataset_fields)
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)

    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'project': project,
                   'dataset': dataset,
                   'datas': dataset_data,
                   'process_types': process_types}

        return render(request, 'ids_projects/datasets/select_data.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        # TODO: this is probably not the best way to do this
        body = urllib.unquote(request.body)

        selected_data = []

        if body:
            response_tuples = map(lambda x: (x.split('=')[0], x.split('=')[1]), body.split('&'))
            selected_data = []
            for key, value in response_tuples:
                selected_data.append(value)

        unselected_data = list(set(project_data) - set(selected_data))
        data_to_remove = filter(lambda x: x in dataset_data, unselected_data)
        data_to_add = list(set(selected_data) - set(dataset_data))

        # remove unselected data
        try:
            if data_to_remove:
                for data_uuid in data_to_remove:
                    data = Data(api_client=api_client, uuid=data_uuid)

                    logger.debug('removing: "%s" from dataset: "%s"' % (data.name, dataset.title))

                    data.remove_container(dataset)
                    data.save()
                    dataset.remove_part(data)

                dataset.save()
        except HTTPError as e:
            exception_msg = 'Unable to remove data from dataset. %s' % e
            logger.error(exception_msg)
            messages.error(request, exception_msg)
            return HttpResponseRedirect(
                reverse('ids_projects:dataset-view',
                        kwargs={'dataset_uuid': dataset.uuid}))

        # add selected data
        try:
            if data_to_add:
                for data_uuid in data_to_add:
                    data = Data(api_client=api_client, uuid=data_uuid)

                    logger.debug('adding: "%s" to dataset: "%s"' % (data.name, dataset.title))

                    data.add_container(dataset)
                    data.save()
                    dataset.add_part(data)

                dataset.save()

            success_msg = 'Successfully added data to dataset.'
            logger.info(success_msg)
            messages.success(request, success_msg)
            return HttpResponseRedirect(reverse('ids_projects:dataset-view', kwargs={'dataset_uuid': dataset.uuid}))

        except HTTPError as e:
            exception_msg = 'Unable to select data. %s' % e
            logger.error(exception_msg)
            messages.error(request, exception_msg)
            return HttpResponseRedirect(
                reverse('ids_projects:dataset-view',
                        kwargs={'dataset_uuid': dataset.uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    """Create a new dataset"""

    project_uuid = request.GET.get('project_uuid', None)

    if not project_uuid:
        messages.warning(request, 'Missing project UUID, cannot find processes.')
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    api_client = request.user.agave_oauth.api_client

    try:
        project = Project(api_client=api_client, uuid=project_uuid)
    except Exception as e:
        exception_msg = 'Unable to load project, cannot create dataset. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        dataset_fields = get_dataset_fields(project)
    except Exception as e:
        exception_msg = 'Missing project type information, cannot create dataset. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:project-view',
                            kwargs={'project_uuid': project.uuid}))

    context = {'project': project}

    # data_choices = [(x.uuid, x.title) for x in project.data]

    #######
    # GET #
    #######
    if request.method == 'GET':

        # context['form_dataset_create'] = DatasetForm(fields=dataset_fields, choices=data_choices)
        context['form_dataset_create'] = DatasetForm(fields=dataset_fields)
        return render(request, 'ids_projects/datasets/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        #form_dataset = DatasetForm(fields=dataset_fields, choices=data_choices, initial=request.POST)
        form_dataset = DatasetForm(dataset_fields, request.POST)

        if form_dataset.is_valid():
            logger.debug('Dataset form is valid')

            try:

                dataset = Dataset(api_client=api_client, value=form_dataset.cleaned_data)
                dataset.save()

                # create two-way relationship to project
                project.add_part(dataset)
                project.save()

                dataset.add_container(project)
                dataset.save()

                success_msg = 'Successfully created dataset.'
                logger.info(success_msg)
                messages.success(request, success_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:dataset-view',
                                    kwargs={'dataset_uuid': dataset.uuid}))
            except HTTPError as e:
                exception_msg = 'Unable to create new dataset. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={'project_uuid': project.uuid}))

        else:
            exception_msg = "Dataset form is not valid!"
            logger.error(exception_msg)
            messages.error(request, exception_msg)
            return HttpResponseRedirect(
                reverse('ids_projects:project-view',
                        kwargs={'project_uuid': project.uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def edit(request, dataset_uuid):
    """Edit existing dataset metadata"""
    api_client = request.user.agave_oauth.api_client

    try:
        dataset = Dataset(api_client=api_client, uuid=dataset_uuid)
        project = dataset.project
    except Exception as e:
        exception_msg = 'Unable to edit dataset. %s' % e
        logger.exception(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/projects/')

    try:
        dataset_fields = get_dataset_fields(project)
    except Exception as e:
        exception_msg = 'Missing project type information, cannot edit dataset. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
            reverse('ids_projects:project-view',
                    kwargs={'project_uuid': project.uuid}))

    # data_choices = [(x.uuid, x.title) for x in project.data]

    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form_dataset_edit': DatasetForm(dataset_fields, dataset.value),
                   'dataset': dataset,
                   'project': project}

        return render(request, 'ids_projects/datasets/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = DatasetForm(dataset_fields, request.POST)

        if form.is_valid():

            try:
                dataset.value.update(form.cleaned_data)
                dataset.save()

                messages.info(request, 'Dataset successfully edited.')
                return HttpResponseRedirect(
                    reverse('ids_projects:dataset-view',
                            kwargs={'dataset_uuid': dataset.uuid}))
            except Exception as e:
                exception_msg = 'Unable to edit specimen. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                    reverse('ids_projects:dataset-view',
                            kwargs={'dataset_uuid': dataset.uuid}))

        else:
            exception_msg = "Dataset form is not valid!"
            logger.error(exception_msg)
            messages.error(request, exception_msg)
            return HttpResponseRedirect(
                reverse('ids_projects:dataset-view',
                        kwargs={'dataset_uuid': dataset.uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def add_data(request, dataset_uuid):
    api_client = request.user.agave_oauth.api_client

    import pdb;
    pdb.set_trace()

    try:
        dataset = Dataset(api_client=api_client, uuid=dataset_uuid)
        project = dataset.project
    except Exception as e:
        exception_msg = 'Unable to load process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))


@login_required
@require_http_methods(['GET', 'POST'])
def remove_data(request, dataset_uuid):
    # TODO: this is not done
    logger.warning('Remove Data not implemented, see Dataset view.')
    return HttpResponseNotFound()


@login_required
@require_http_methods(['GET'])
def make_public(request, dataset_uuid):
    # TODO: this is not done
    logger.warning('Make Public not implemented, see Dataset view.')
    return HttpResponseNotFound()


@login_required
@require_http_methods(['GET'])
def make_private(request, dataset_uuid):
    # TODO: this is not done
    logger.warning('Make Private not implemented, see Dataset view.')
    return HttpResponseNotFound()


# @login_required
@require_http_methods(['GET', 'POST'])
def request_doi(request, dataset_uuid):
    # # TODO: this is not done
    # logger.warning('Request DOI not implemented, see Dataset view.')
    # return HttpResponseNotFound()

    
    if request.method == 'GET':
        context = {}
        if request.user.is_anonymous():
            api_client = get_portal_api_client()
        else:
            api_client = request.user.agave_oauth.api_client

        try:
            dataset = Dataset(api_client=api_client, uuid=dataset_uuid)
            essential = meta_for_doi(dataset)
            builder = identifierBuilder()
            builder.buildXML(essential)
            xmlObject = builder.getXML()

            # requesting doi
            client = ezidClient('apitest', 'apitest')            
            metadata = {}
            metadata["datacite"] = ET.tostring(xmlObject, encoding = "UTF-8", method = "xml")                       
            response = client.Mint('doi:10.5072/FK2', metadata)
            doi = response.split('|')[0].strip()
            ark = response.split('|')[1].strip()
            
            # update generated ARK as alternative identifier
            essential_new = update_alternateIdentifier(essential, ark)
            builder.setAlternateIdentifiers(essential_new)
            xmlObject = builder.getXML()
            metadata["datacite"] = ET.tostring(xmlObject, encoding = "UTF-8", method = "xml")            
            response = client.Update(doi, metadata)            

            context['doi'] = doi
            context['ark'] = ark

            return render(request, 'ids_projects/datasets/request_doi.html', context)

        except Exception as e:
            exception_msg = 'Unable to load process. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))                    


def meta_for_doi(dataset):
    """ constructing json for build xml object """
    project = dataset.project

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
    print json.dumps(metadata, indent = 2)
    return metadata

def update_alternateIdentifier(essential_meta, ark):
    alternateIdentifiers = []
    alternateIdentifier = {}
    alternateIdentifier['alternateIdentifierType'] = 'ARK'
    alternateIdentifier['text'] = ark
    alternateIdentifiers.append(alternateIdentifier)

    essential_meta['alternateIdentifiers'] = alternateIdentifiers
    print json.dumps(essential_meta, indent = 2)
    return essential_meta


@login_required
@require_http_methods(['GET'])
def delete(request, dataset_uuid):
    """Delete a dataset - if no external identifier is associated with it"""
    next_url = request.GET.get('next_url', None)
    api_client = request.user.agave_oauth.api_client

    try:
        dataset = Dataset(api_client=api_client, uuid=dataset_uuid)

        if next_url is None:
            containers = dataset.containers
            container = next(iter(containers), None)
            if container:
                name = container.name[6:]
                next_url = reverse('ids_projects:%s-view' % name,
                                   kwargs={'%s_uuid' % name: container.uuid})

        dataset.delete()

        if next_url is not None:
            return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    except Exception as e:
        exception_msg = 'Unable to load data. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))
