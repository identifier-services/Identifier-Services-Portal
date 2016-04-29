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
from ..models import Project, Specimen, Process
from helper import client, collapse_meta
from requests import HTTPError


logger = logging.getLogger(__name__)


@login_required
def list(request):
    """List all processes related to a specimen"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        specimen_uuid = request.GET.get('specimen_uuid', None)
        specimen = Specimen(uuid = specimen_uuid)
        context = { 'project': specimen.project,
                    'specimen' : specimen,
                    'processes': specimen.processes
                  }

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

        process = Process(uuid = process_uuid)

        context = {'process' : process,
                   'project' : process.project,
                   'specimen' : process.specimen,
                   'datas' : process.data}

        return render(request, 'ids_projects/processes/detail.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def create(request):
    """Create a new process related to a specimen"""
    specimen_uuid = request.GET.get('specimen_uuid', None)
    specimen = Specimen(uuid=specimen_uuid)

    project = specimen.project
    investigation_type = project.value['investigation_type'].lower()

    object_descriptions = getattr(settings, 'OBJ_DESCR')
    investigation_types = object_descriptions['investigation_types']

    project_description = investigation_types[investigation_type]
    project_processes = project_description['processes']

    process_type_choices = [('', 'Choose one'),] + \
                            [(x,x.title()) for x in project_processes.keys()]

    context = {'specimen':specimen}

    #######
    # GET #
    #######
    if request.method == 'GET':
        context['form_a'] = form_a = ProcessTypeForm(process_type_choices)
        context['form_b'] = None

    ########
    # POST #
    ########
    elif request.method == 'POST':

        process_type = request.POST.get('process_type')
        process_fields = project_processes[process_type]['fields']

        form_a = ProcessTypeForm(process_type_choices, request.POST)
        form_a.fields['process_type'].widget.attrs['readonly'] = True

        # bug fix, if we disable this field, we won't get the value on the next post
        # form_a.fields['process_type'].widget.attrs['disabled'] = True

        ######################################
        # POST includes 'form_a' fields only #
        ######################################
        if not 'process_fields' in request.POST:
            form_b = ProcessFieldsForm(process_fields)
            context['form_a'] = form_a
            context['form_b'] = form_b

        ########################################
        # POST includes form_a & form_b fields #
        ########################################
        else:
            form_b = ProcessFieldsForm(process_fields, request.POST)

            if form_a.is_valid() and form_b.is_valid():
                logger.debug('Process form is valid')

                data = {'process_type':process_type}
                data.update(form_a.cleaned_data.copy())
                data.update(form_b.cleaned_data.copy())

                associationIds = specimen.associationIds
                associationIds.append(specimen.uuid)

                new_process = Process()
                new_process.associationIds = associationIds
                new_process.value = data

                try:
                    response = new_process.save()
                    process_uuid = response['uuid']
                    logger.debug('Successfully created process: {}'.format(process_uuid))
                    messages.success(request, 'Successfully created process.')
                    return HttpResponseRedirect('/process/{}'.format(process_uuid))
                except HTTPError as e:
                    logger.debug('Error while attempting to create process metadata: %s' % e)
                    messages.error(request, 'Encountered error, process not created.')
                    return HttpResponseRedirect('/specimen/{}'.format(specimen_uuid))

    if request.is_ajax():
        return render(request, 'ids_projects/processes/get_fields_ajax.html', context)
    else:
        return render(request, 'ids_projects/processes/create.html', context)


@login_required
def edit(request, process_uuid):
    """Edit existing process metadata"""
    try:
        process = Process(uuid=process_uuid)
    except HTTPError as e:
        logger.error('Error editing process. {}'.format(e.message))
        messages.error(request, 'Error editing process.')
        return HttpResponseRedirect('/process/{}'.format(process_uuid))
    except Exception as e:
        logger.error('Error editing process. {}'.format(e.message))
        messages.error(request, 'Process not found.')
        return HttpResponseRedirect('/projects/')

    # TODO: find better way of getting process fields.
    object_descriptions = getattr(settings, 'OBJ_DESCR')
    investigation_types = object_descriptions['investigation_types']
    investigation_type = process.project.value['investigation_type'].lower()

    project_description = investigation_types[investigation_type]
    project_processes = project_description['processes']
    process_type = process.value['process_type']
    process_fields = project_processes[process_type]['fields']

    #######
    # GET #
    #######
    if request.method == 'GET':
        context = {'form': ProcessFieldsForm(process_fields, initial=process.body),
                   'specimen': process.specimen,
                   'project': process.project,
                   'process': process}

        return render(request, 'ids_projects/processes/edit.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':
        form = ProcessFieldsForm(process_fields, request.POST)

        if form.is_valid():
            try:
                process.value = form.cleaned_data.copy()
                process.save()
                logger.error('Successfully edited process.')
                messages.error(request, 'Successfully edited process.')
                return HttpResponseRedirect('/process/{}'.format(process_uuid))
            except HTTPError as e:
                logger.error('Error editing process. {}'.format(e.message))
                messages.error(request, 'Error editing process.')
                return HttpResponseRedirect('/process/{}'.format(process_uuid))


@login_required
def _edit(request, process_uuid):
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
    process = Process(uuid=process_uuid)

    # TODO: delete data, or just associate data with project?
    for data in process.data:
        # remove process_uuid from associationIds on data, leaving only project_uuid
        try:
            data.associationIds.remove(process_uuid)
        except HTTPError as e:
            logger.debug('Error while attempting to remove process_uuid from data metadata: %s' % e)

    try:
        project = process.project
        specimen = process.specimen
        process.delete()
        messages.success(request, 'Successfully deleted process.')
    except HTTPError as e:
        logger.debug('Error while attempting to delete process metadata: %s' % e)
        messages.success(request, 'Encountered error while attempting to delete process.')

    if specimen:
        return HttpResponseRedirect('/specimen/{}'.format(specimen.uuid))
    else:
        return HttpResponseRedirect('/project/{}'.format(project.uuid))
