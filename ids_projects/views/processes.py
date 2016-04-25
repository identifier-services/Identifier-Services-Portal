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
from ..forms.processes import ProcessTypeForm, ProcessFieldsForm
from helper import client, collapse_meta


logger = logging.getLogger(__name__)


@login_required
def list(request):
    """List all processes related to a specimen"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        specimen_uuid = request.GET.get('specimen_uuid', False)

        a = client(request)
        process_query = {'name':'idsvc.process','associationIds':'{}'.format(specimen_uuid)}
        process_raw = a.meta.listMetadata(q=json.dumps(process_query))
        processes = map(collapse_meta, process_raw)

        context = {'processes' : processes, 'specimen_uuid': specimen_uuid}

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

        # find data associated with the process
        query = {'associationIds': process_uuid }
        results_raw = a.meta.listMetadata(q=json.dumps(query))
        # results = map(collapse_meta, results_raw)
        results = results_raw

        datas = []
        for result in results:
            if result['name'] == 'idsvc.data':
                datas.append(result)

        context = {'process' : process,
                   'project' : project,
                   'specimen' : specimen,
                   'datas' : datas}

        return render(request, 'ids_projects/processes/detail.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def create(request):
    """Create a new process related to a specimen"""

    specimen_uuid = None

    if request.method == 'GET':
        specimen_uuid = request.GET.get('specimen_uuid')
    elif request.method == 'POST':
        specimen_uuid = request.POST.get('specimen_uuid')

    ###
    # we need to get the project so that we know what types of processes to list
    ###

    # get association ids
    a = client(request)
    specimen_raw = a.meta.getMetadata(uuid=specimen_uuid)
    specimen = collapse_meta(specimen_raw)
    associationIds = specimen['associationIds']
    project = None

    # find the project
    query = {'uuid': {'$in': associationIds}}
    results_raw = a.meta.listMetadata(q=json.dumps(query))
    results = map(collapse_meta, results_raw)
    for result in results:
        if result['name'] == 'idsvc.project':
            project = result

    investigation_type = project['investigation_type'].lower()

    ###
    # now that we know the type of project, we can list relevant process types
    ###

    object_descriptions = getattr(settings, 'OBJ_DESCR')
    investigation_types = object_descriptions['investigation_types']
    project_description = investigation_types[investigation_type]
    project_processes = project_description['processes']
    process_type_list = [(x,x.title()) for x in project_processes.keys()]
    process_type_list = [('', 'Choose one'),] + process_type_list
    context = {'project': project,
               'specimen': specimen,
               'process': None}

    ########
    # POST #
    ########
    if request.method == 'POST':

        process_fields = []
        if 'process_type' in request.POST:
            process_type = request.POST.get('process_type')
            process_fields = project_processes[process_type]['fields']

        form_a = ProcessTypeForm(process_type_list, request.POST)
        form_a.fields['process_type'].widget.attrs['readonly'] = True
        form_a.fields['process_type'].widget.attrs['disabled'] = True

        import pdb; pdb.set_trace()

        if 'type_selected' in request.POST:
            form_b = ProcessFieldsForm(process_fields, request.POST)
        else:
            form_b = ProcessFieldsForm(process_fields)

        # add specimen uuid to association ids
        associationIds.append(specimen_uuid)

        if not request.is_ajax():
            if form_a.is_valid() and form_b.is_valid():
                data = form_a.cleaned_data.copy()
                data.update(form_b.cleaned_data.copy())

                logger.debug('Process form is valid')

                new_process = {
                    "name":"idsvc.process",
                    "associationIds": associationIds,
                    "value": data
                }

                try:
                    response = a.meta.addMetadata(body=new_process)
                except Exception as e:
                    logger.debug('Error while attempting to create process metadata: %s' % e)
                else:
                    messages.success(request, 'Successfully created process.')
                    return HttpResponseRedirect('/process/{}'.format(response['uuid']))

    else:
        form_a = ProcessTypeForm(process_type_list)
        form_b = None

    context['form_a'] = form_a
    context['form_b'] = form_b

    if request.is_ajax():
        return render(request, 'ids_projects/processes/get_fields_ajax.html', context)
    else:
        return render(request, 'ids_projects/processes/create.html', context)


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
