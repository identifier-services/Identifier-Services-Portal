from agavepy.agave import Agave, AgaveException
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import (HttpResponse,
                         HttpResponseRedirect,
                         HttpResponseBadRequest,
                         HttpResponseForbidden,
                         HttpResponseNotFound,
                         HttpResponseServerError)
from django.shortcuts import render
import json, logging
from ..forms.specimens import SpecimenForm


logger = logging.getLogger(__name__)


def _client(request):
    token = request.session.get(getattr(settings, 'AGAVE_TOKEN_SESSION_ID'))
    access_token = token.get('access_token', None)
    url = getattr(settings, 'AGAVE_TENANT_BASEURL')
    return Agave(api_server = url, token = access_token)


def _collaps_meta(x):
    d = x['value']
    d['uuid'] = x['uuid']
    return d


def list(request, project_id):
    """List all specimens related to a project"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = _client(request)
        specimens_query = {'name':'idsvc.specimen','associationIds':'{}'.format(project_id)}
        specimens_raw = a.meta.listMetadata(q=json.dumps(specimens_query))
        specimens = map(_collaps_meta, specimens_raw)

        context = {'specimens' : specimens}

        return render(request, 'ids_projects/specimens/index.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


def view(request, specimen_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = _client(request)
        specimen_raw = a.meta.getMetadata(uuid=specimen_id)
        specimen = _collaps_meta(specimen_raw)

        # for specimen in specimens:
        #     specimen_id = specimen['uuid']
        #     process_query = {'name':'idsvc.process','associationIds':'{}'.format(specimen_id)}
        #     processes_raw = a.meta.listMetadata(q=json.dumps(specimens_query))
        #     processes = map(_collaps_meta, processes_raw)
        #     for process in processes:
        #         process_id = process['uuid']
        #         files_query = {'name':'idsvc.data','associationIds':'{}'.format(process_id)}
        #         files_raw = a.meta.listMetadata(q=json.dumps(files_query))
        #         files = map(_collaps_meta, files_raw)
        #         process['files'] = files
        #     specimen['processes'] = processes
        # project['specimens'] = specimens

        context = {'specimen' : specimen,}

        print context

        #return HttpResponse(json.dumps(context),status = 200, content_type='application/json')
        return render(request, 'ids_projects/specimens/detail.html', context)


    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


def create(request, project_id):
    """Create a new specimen related to a project"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form': SpecimenForm(), 'project_id': project_id}

        return render(request, 'ids_projects/specimens/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = SpecimenForm(request.POST)

        if form.is_valid():

            taxon_name = form.cleaned_data['taxon_name']
            specimen_id = form.cleaned_data['specimen_id']
            organ_or_tissue = form.cleaned_data['organ_or_tissue']
            developmental_stage = form.cleaned_data['developmental_stage']
            haploid_chromosome_count = form.cleaned_data['haploid_chromosome_count']
            ploidy = form.cleaned_data['ploidy']
            propagation = form.cleaned_data['propagation']
            estimated_genome_size = form.cleaned_data['estimated_genome_size']

            new_specimen = {
                "name":"idsvc.specimen",
                "associationIds": project_id,
                "value": {
                    "taxon_name":taxon_name,
                    "specimen_id":specimen_id,
                    "organ_or_tissue":organ_or_tissue,
                    "developmental_stage":developmental_stage,
                    "haploid_chromosome_count":haploid_chromosome_count,
                    "ploidy":ploidy,
                    "propagation":propagation,
                    "estimated_genome_size":estimated_genome_size,
                }
            }

            a = _client(request)
            try:
                response = a.meta.addMetadata(body=new_specimen)
            except Exception as e:
                logger.debug('Error while attempting to create specimen metadata: %s' % e)
            else:
                messages.success(request, 'Successfully created specimen.')
                return HttpResponseRedirect('/specimen/{}'.format(response['uuid']))

        messages.info(request, 'Did not create new specimen.')
        return HttpResponseRedirect('/project/{}'.format(project_id))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


def edit(request, specimen_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = _client(request)
        query = {'uuid':project_id}
        project_list = a.meta.listMetadata(q=json.dumps(query))

        try:
            project = project_list[0]
        except:
            return HttpResponseNotFound("Project not found")
        else:
            return HttpResponse(json.dumps(project), content_type="application/json", status=200)

    ########
    # POST #
    ########
    elif request.method == 'POST':
        return HttpResponse("Creating new project: {}".format(len(projects)+1))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


def delete(request, specimen_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = _client(request)
        specimens_query = {
            'name':'idsvc.specimen',
            'associationIds':'{}'.format(project_id)
        }
        specimens_list = a.meta.listMetadata(q=json.dumps(specimens_query))

        return HttpResponse(json.dumps(specimens_list),
            content_type="application/json", status=200)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")
