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
def list(request, specimen_uuid):
    """List all processes related to a specimen"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = client(request)
        process_query = {'name':'idsvc.process','associationIds':'{}'.format(specimen_uuid)}
        process_raw = a.meta.listMetadata(q=json.dumps(specimens_query))
        processes = map(collapse_meta, process_raw)

        context = {'processes' : specimens, 'specimen_uuid': specimen_uuid}

        return render(request, 'ids_projects/processes/index.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def view(request, process_uuid):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        # get the process
        a = client(request)
        process_raw = a.meta.getMetadata(uuid=process_uuid)
        process = collapse_meta(process_raw)

        project = None
        specimen = None

        # find project & specimen the process is associated with
        associationIds = process['associationIds']
        query = {'uuid': { '$in': associationIds }}
        results_raw = a.meta.listMetadata(q=json.dumps(query))
        results = map(collapse_meta, results_raw)
        for result in results:
            if result['name'] == 'idsvc.specimen':
                specimen = result
            if result['name'] == 'idsvc.project':
                project = result

        context = {'process' : process,
                   'project' : project,
                   'specimen' : specimen}

        return render(request, 'ids_projects/processes/detail.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def create(request, specimen_uuid):
    """Create a new process realted to a specimen"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        # get association ids
        a = client(request)
        specimen_raw = a.meta.getMetadata(uuid=specimen_uuid)
        specimen = collapse_meta(specimen_raw)
        associationIds = specimen['associationIds']

        project = None

        # find the project
        query = {'uuid': { '$in': associationIds }}
        results_raw = a.meta.listMetadata(q=json.dumps(query))
        results = map(collapse_meta, results_raw)
        for result in results:
            if result['name'] == 'idsvc.project':
                project = result

        context = {'form': ProcessForm(),
                   'project': project,
                   'specimen': specimen,
                   'process': None}

        return render(request, 'ids_projects/processes/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = ProcessForm(request.POST)

        # inherit specimen association ids
        a = client(request)
        specimen_raw = a.meta.getMetadata(uuid=specimen_uuid)
        specimen = collapse_meta(specimen_raw)
        associationIds = specimen['associationIds']

        project = None

        # find the project
        query = {'uuid': { '$in': associationIds }}
        results_raw = a.meta.listMetadata(q=json.dumps(query))
        results = map(collapse_meta, results_raw)
        for result in results:
            if result['name'] == 'idsvc.project':
                project = result

        # add specimen uuid to association ids
        associationIds.append(specimen_uuid)

        if form.is_valid():

            logger.debug('Process form is valid')

            process_type = form.cleaned_data['process_type']
            sequence_method = form.cleaned_data['sequence_method']
            sequence_hardware = form.cleaned_data['sequence_hardware']
            assembly_method = form.cleaned_data['assembly_method']
            reference_sequence = form.cleaned_data['reference_sequence']
            # associationIds = form.cleaned_data['associationIds']
            # project_uuid = form.cleaned_data['project_uuid']

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
        # return HttpResponseRedirect('/specimen/{}'.format(specimen_uuid))
        return HttpResponseRedirect('/project/{}'.format(project.uuid))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def edit(request, process_uuid):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = client(request)
        try:
            # get the process metadata object
            process_raw = a.meta.getMetadata(uuid=process_uuid)
            process = collapse_meta(process_raw)
        except:
            logger.error('Error editing process. {}'.format(e.message))
            messages.error(request, 'Process not found.')

            return HttpResponseRedirect('/projects/')
        else:
            project = None
            specimen = None

            # find the project and specimen that the process is associated with
            associationIds = process['associationIds']
            query = {'uuid': { '$in': associationIds }}
            results_raw = a.meta.listMetadata(q=json.dumps(query))
            results = map(collapse_meta, results_raw)
            for result in results:
                if result['name'] == 'idsvc.project':
                    project = result
                if result['name'] == 'idsvc.specimen':
                    specimen = result

            context = {'form': ProcessForm(initial=process),
                       'specimen': specimen,
                       'project': project,
                       'process': process}

            return render(request, 'ids_projects/processes/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        # get the association fields
        # TODO: I need to store this in hidden form field, but having trouble with that.
        a = client(request)
        try:
            # get the specimen metadata object
            process_raw = a.meta.getMetadata(uuid=process_uuid)
            process = collapse_meta(process_raw)
        except:
            logger.error('Error editing specimen. {}'.format(e.message))
            messages.error(request, 'Process not found.')

            return HttpResponseRedirect('/projects/')
        else:
            associationIds = process['associationIds']

        form = ProcessForm(request.POST)

        if form.is_valid():

            logger.debug('Process form is valid')

            process_type = form.cleaned_data['process_type']
            sequence_method = form.cleaned_data['sequence_method']
            sequence_hardware = form.cleaned_data['sequence_hardware']
            assembly_method = form.cleaned_data['assembly_method']
            reference_sequence = form.cleaned_data['reference_sequence']

            new_process = {
                "name" : 'idsvc.process',
                "associationIds" : associationIds,
                "value": {
                    "process_type":process_type,
                    "sequence_method":sequence_method,
                    "sequence_hardware":sequence_hardware,
                    "assembly_method":assembly_method,
                    "reference_sequence":reference_sequence
                }
            }

            try:
                response = a.meta.updateMetadata(uuid=process_uuid, body=new_process)
            except Exception as e:
                logger.debug('Error while attempting to edit process metadata: %s' % e)
                messages.error(request, 'Error while attempting to edit process.')
            else:
                messages.success(request, 'Successfully edited process.')
                return HttpResponseRedirect('/process/{}'.format(response['uuid']))

        else:

            logger.debug('Process form is not valid')

        messages.info(request, 'Did not edit process.')
        return HttpResponseRedirect('/process/{}'.format(process_uuid))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def delete(request, process_uuid):
    """Delete a process"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        # TODO: Ask user if file data should be deleted

        # get the process
        a = client(request)
        process_raw = a.meta.getMetadata(uuid=process_uuid)
        process = collapse_meta(process_raw)

        project = None
        specimen = None

        # find project & specimen the process is associated with
        associationIds = process['associationIds']
        query = {'uuid': { '$in': associationIds }}
        results_raw = a.meta.listMetadata(q=json.dumps(query))
        results = map(collapse_meta, results_raw)
        for result in results:
            if result['name'] == 'idsvc.specimen':
                specimen = result
            if result['name'] == 'idsvc.project':
                project = result

        try:
            a.meta.deleteMetadata(uuid=process_uuid)
        except Exception as e:
            logger.error('Error deleting process. {}'.format(e.message) )
            messages.error(request, 'Process deletion unsuccessful.')
            # return HttpResponseServerError("Error deleting project.")
            if specimen:
                return HttpResponseRedirect('/specimen/{}'.format(specimen['uuid']))
            if project:
                return HttpResponseRedirect('/project/{}'.format(project['uuid']))
            else:
                return HttpResponseRedirect('/projects/')
        else:
            messages.success(request, 'Successfully deleted process.')
            if specimen:
                return HttpResponseRedirect('/specimen/{}'.format(specimen['uuid']))
            if project:
                return HttpResponseRedirect('/project/{}'.format(project['uuid']))
            else:
                return HttpResponseRedirect('/projects/')

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")
