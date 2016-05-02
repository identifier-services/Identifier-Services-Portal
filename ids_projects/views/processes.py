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

    context = { 'project':project,
                'specimen':specimen }

    #######
    # GET #
    #######
    if request.method == 'GET':
        context['form_process_type'] = form_process_type = ProcessTypeForm(process_type_choices)
        context['form_process_fields'] = None

    ########
    # POST #
    ########
    elif request.method == 'POST':

        process_type = request.POST.get('process_type')
        process_fields = project_processes[process_type]['fields']

        form_process_type = ProcessTypeForm(process_type_choices, request.POST)
        form_process_type.fields['process_type'].widget.attrs['readonly'] = True

        # bug fix, if we disable this field, we won't get the value on the next post
        # form_process_type.fields['process_type'].widget.attrs['disabled'] = True

        ######################################
        # POST includes 'form_process_type' fields only #
        ######################################
        if not 'process_fields' in request.POST:
            form_process_fields = ProcessFieldsForm(process_fields)
            context['form_process_type'] = form_process_type
            context['form_process_fields'] = form_process_fields

        ########################################
        # POST includes form_process_type & form_process_fields fields #
        ########################################
        else:
            form_process_fields = ProcessFieldsForm(process_fields, request.POST)

            if form_process_type.is_valid() and form_process_fields.is_valid():
                logger.debug('Process form is valid')

                data = {'process_type':process_type}
                data.update(form_process_type.cleaned_data.copy())
                data.update(form_process_fields.cleaned_data.copy())

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
        context = {'form_process_edit': ProcessFieldsForm(process_fields, initial=process.body),
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
