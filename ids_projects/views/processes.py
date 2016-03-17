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
from ..forms.processes import ProcessForm
from helper import client, collapse_meta


logger = logging.getLogger(__name__)


@login_required
def list(request, specimen_id):
    """List all processes related to a specimen"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = client(request)
        process_query = {'name':'idsvc.process','associationIds':'{}'.format(specimen_id)}
        process_raw = a.meta.listMetadata(q=json.dumps(specimens_query))
        processes = map(collapse_meta, process_raw)

        context = {'processes' : specimens, 'specimen_id': specimen_id}

        return render(request, 'ids_projects/processes/index.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def view(request, process_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = client(request)
        process_raw = a.meta.getMetadata(uuid=process_id)
        process = collapse_meta(process_raw)

        # for specimen in specimens:
        #     specimen_id = specimen['uuid']
        #     process_query = {'name':'idsvc.process','associationIds':'{}'.format(specimen_id)}
        #     processes_raw = a.meta.listMetadata(q=json.dumps(specimens_query))
        #     processes = map(collapse_meta, processes_raw)
        #     for process in processes:
        #         process_id = process['uuid']
        #         files_query = {'name':'idsvc.data','associationIds':'{}'.format(process_id)}
        #         files_raw = a.meta.listMetadata(q=json.dumps(files_query))
        #         files = map(collapse_meta, files_raw)
        #         process['files'] = files
        #     specimen['processes'] = processes
        # project['specimens'] = specimens

        context = {'process' : process,}

        return render(request, 'ids_projects/processes/detail.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def create(request, specimen_id):
    """Create a new process realted to a specimen"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        # get association ids
        a = client(request)
        specimen = a.meta.getMetadata(uuid=specimen_id)
        associationIds = specimen['associationIds']

        # find which is project id
        query = {'associationIds': { '$in': associationIds }}
        results = a.meta.listMetadata(q=json.dumps(query))
        project_id = None
        for result in results:
            if result.name == 'idsvc.project':
                project_id == result.uuid

        context = {'form': ProcessForm(),
                   'project_id': project_id,
                   'specimen_id': specimen_id,
                   'none_test': None}

        return render(request, 'ids_projects/processes/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = ProcessForm(request.POST)

        # inherit specimen association ids
        a = client(request)
        specimen = a.meta.getMetadata(uuid=specimen_id)
        associationIds = specimen['associationIds']

        logger.debug('associationIds: {}'.format(associationIds))

        # find which is project id
        query = {'uuid': { '$in': associationIds }}
        results = a.meta.listMetadata(q=json.dumps(query))

        logger.debug('results: {}'.format(results))

        project_id = None
        for result in results:

            if result['name'] == 'idsvc.project':
                project_id == result['uuid']

        # add specimen uuid to association ids
        associationIds.append(specimen_id)

        if form.is_valid():

            logger.debug('Process form is valid')

            process_type = form.cleaned_data['process_type']
            sequence_method = form.cleaned_data['sequence_method']
            sequence_hardware = form.cleaned_data['sequence_hardware']
            assembly_method = form.cleaned_data['assembly_method']
            reference_sequence = form.cleaned_data['reference_sequence']
            # associationIds = form.cleaned_data['associationIds']
            # project_id = form.cleaned_data['project_id']

            new_process = {
                "name":"idsvc.process",
                "associationIds": associationIds,
                "value": {
                    "process_type":process_type,
                    "sequence_method":sequence_method,
                    "sequence_hardware":sequence_hardware,
                    "assembly_method":assembly_method,
                    "reference_sequence":reference_sequence
                }
            }

            try:
                response = a.meta.addMetadata(body=new_process)
            except Exception as e:
                logger.debug('Error while attempting to create process metadata: %s' % e)
            else:
                messages.success(request, 'Successfully created process.')
                return HttpResponseRedirect('/process/{}'.format(response['uuid']))

        else:

            logger.debug('Process form is not valid')

        messages.info(request, 'Did not create new process.')
        # return HttpResponseRedirect('/specimen/{}'.format(specimen_id))
        return HttpResponseRedirect('/project/{}'.format(project_id))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def edit(request, process_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = client(request)
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


@login_required
def delete(request, prodess_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = client(request)
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
