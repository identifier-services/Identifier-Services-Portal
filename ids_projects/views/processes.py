from agavepy.agave import Agave, AgaveException
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
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
        if not specimen_uuid:
            messages.warning(request, 'Missing specimen UUID, cannot find processes.')
            return HttpResponseRedirect(reverse('ids_projects:project-list'))

        try:
            specimen = Specimen(uuid=specimen_uuid, user=request.user)
        except Exception as e:
            exception_msg = 'Unable to load specimen, processes. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(reverse('ids_projects:project-list'))

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

        try:
            process = Process(uuid=process_uuid, user=request.user)
        except Exception as e:
            exception_msg = 'Unable to load process. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(reverse('ids_projects:project-list'))

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
    if not specimen_uuid:
        messages.warning(request, 'Missing specimen UUID, cannot create processes.')
        return HttpResponseRedirect(reverse('ids_projects:project-list'))

    try:
        specimen = Specimen(uuid=specimen_uuid, user=request.user)
    except Exception as e:
        exception_msg = 'Unable to load specimen, cannot create process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list'))

    try:
        project = specimen.project
        investigation_type = project.value['investigation_type'].lower()

        object_descriptions = getattr(settings, 'OBJ_DESCR')
        investigation_types = object_descriptions['investigation_types']

        project_description = investigation_types[investigation_type]
        project_processes = project_description['processes']

        process_type_choices = [('', 'Choose one'),] + \
                                [(x,x.title()) for x in project_processes.keys()]
    except Exception as e:
        exception_msg = 'Missing project type information, cannot create process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:specimen-view',
                            kwargs={'specimen_uuid': specimen.uuid}))

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
        form_process_type.fields['process_type'].widget.attrs['disabled'] = True
        form_process_type.fields['process_type'].widget.attrs['readonly'] = True


        #################################################
        # POST includes 'form_process_type' fields only #
        #################################################
        if not 'process_fields' in request.POST:
            form_process_fields = ProcessFieldsForm(process_fields)
            context['form_process_type'] = form_process_type
            context['form_process_fields'] = form_process_fields
            context['process_type'] = process_type

        ################################################################
        # POST includes form_process_type & form_process_fields fields #
        ################################################################
        else:
            form_process_fields = ProcessFieldsForm(process_fields, request.POST)

            if form_process_type.is_valid() and form_process_fields.is_valid():
                logger.debug('Process form is valid')

                data = {'process_type':process_type}
                data.update(form_process_type.cleaned_data.copy())
                data.update(form_process_fields.cleaned_data.copy())

                associationIds = specimen.associationIds
                associationIds.append(specimen.uuid)

                body = { 'associationIds': associationIds, 'value': data }

                try:
                    process = Process(initial_data=body, user=request.user)
                    result = process.save()
                except HTTPError as e:
                    exception_msg = 'Unable to create new process. %s' % e
                    logger.error(exception_msg)
                    messages.warning(request, exception_msg)
                    return HttpResponseRedirect(
                                reverse('ids_projects:specimen-view',
                                        kwargs={'specimen_uuid': specimen.uuid}))

                if 'uuid' in result:
                    success_msg = 'Successfully created process.'
                    logger.info(success_msg)
                    messages.success(request, success_msg)
                    return HttpResponseRedirect(
                                reverse('ids_projects:process-view',
                                        kwargs={'process_uuid': process.uuid}))

            warning_msg = 'Invalid API response. %s' % result
            logger.warning(warning_msg)
            messages.warning(request, warning_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:specimen-view',
                                kwargs={'specimen_uuid': specimen.uuid}))

    if request.is_ajax():
        return render(request, 'ids_projects/processes/get_fields_ajax.html', context)
    else:
        return render(request, 'ids_projects/processes/create.html', context)


@login_required
def edit(request, process_uuid):
    """Edit existing process metadata"""
    try:
        process = Process(uuid=process_uuid, user=request.user)
    except HTTPError as e:
        logger.error('Error editing process. {}'.format(e.message))
        messages.warning(request, 'Error editing process.')
        return HttpResponseRedirect('/process/{}'.format(process_uuid))
    except Exception as e:
        logger.error('Error editing process. {}'.format(e.message))
        messages.warning(request, 'Process not found.')
        return HttpResponseRedirect('/projects/')

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
                # will not overwrite association ids
                body = { 'value': form.cleaned_data }
                process.set_initial(body)
                result = process.save()
            except Exception as e:
                exception_msg = 'Unable to edit process. %s' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:process-view',
                                    kwargs={'process_uuid': process.uuid}))

            if 'uuid' in result:
                messages.info(request, 'Process successfully edited.')
                return HttpResponseRedirect(
                            reverse('ids_projects:process-view',
                                    kwargs={'process_uuid': process.uuid}))

            warning_msg = 'Invalid API response. %s' % result
            logger.warning(warning_msg)
            messages.warning(request, warning_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:process-view',
                                kwargs={'process_uuid': process.uuid}))

@login_required
def delete(request, process_uuid):
    """Delete a process"""
    process = Process(uuid=process_uuid, user=request.user)

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
