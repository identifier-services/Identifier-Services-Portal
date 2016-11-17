from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from ..forms.processes import ProcessTypeForm, ProcessFieldsForm, AddRelationshipForm
from ..models import Project, Specimen, Process
from ids.utils import (get_portal_api_client,
                       get_process_type_keys,
                       get_process_choices,
                       get_process_fields)
from requests import HTTPError

from ..forms.upload_option import UploadOptionForm, UploadFileForm
from ids_projects.tasks import bulk_ISH_registration

import traceback
import csv
import logging

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET'])
def list(request):
    """List all processes related to a specimen"""
    api_client = request.user.agave_oauth.api_client

    project_uuid = request.GET.get('project_uuid', None)
    specimen_uuid = request.GET.get('specimen_uuid', None)

    if not specimen_uuid and not project_uuid:
        messages.warning(request, 'Missing project or specimen UUID, cannot find processes.')
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    project = None
    specimen = None
    process = None

    try:
        if not specimen_uuid:
            project = Project(api_client=api_client, uuid=project_uuid)
            processes = project.processes
        else:
            specimen = Specimen(api_client=api_client, uuid=specimen_uuid)
            processes = specimen.processes
            project = Specimen.project

    except Exception as e:
        exception_msg = 'Unable to load project, specimen, or processes. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    context = { 'project': project,
                'specimen' : specimen,
                'processes': processes
              }

    return render(request, 'ids_projects/processes/index.html', context)


@login_required
@require_http_methods(['GET'])
def view(request, process_uuid):
    """ """
    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    try:
        process = Process(api_client=api_client, uuid=process_uuid)
        project = process.project
        specimen = process.specimen
        data = process.data
        inputs = process.inputs
        outputs = process.outputs
    except Exception as e:
        exception_msg = 'Unable to load process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        process_types = get_process_type_keys(project)
        process_fields = get_process_fields(project, process.value['process_type'])
        process.set_fields(process_fields)
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)

    context = {'process': process,
               'project': project,
               'specimen': specimen,
               'datas': data,
               'inputs': inputs,
               'outputs': outputs,
               'process_types': process_types }

    return render(request, 'ids_projects/processes/detail.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    """Create a new process related to a specimen"""

    # get parent uuid (project or specimen), and process type, if inlcuded in
    # the query string

    project_uuid = request.GET.get('project_uuid', None)
    specimen_uuid = request.GET.get('specimen_uuid', None)
    process_type = request.GET.get('process_type', None)

    # check to make sure we have at least one parent uuid (project or specimen)

    if not specimen_uuid and not project_uuid:
        messages.warning(request, 'Missing project or specimen UUID, cannot find processes.')
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    # get the api_client to pass to the model for communication with agave

    api_client = request.user.agave_oauth.api_client

    # instantiate either a project and a specimen, or just a project (specimen
    # objects always have a parent project)

    try:
        if not specimen_uuid:
            specimen = None
            project = Project(api_client=api_client, uuid=project_uuid)
        else:
            specimen = Specimen(api_client=api_client, uuid=specimen_uuid)
            project = specimen.project
    except Exception as e:
        exception_msg = 'Unable to load project or specimen, cannot create process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    if project is None:
        exception_msg = 'Missing project, cannot create process.'
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    # add project, specimen to the form context

    context = {'project': project,
               'specimen': specimen}

    # get the different types of processes we can create for this project type

    try:
        process_type_choices = get_process_choices(project)
    except Exception as e:
        exception_msg = 'Missing project type information, cannot create process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:specimen-view',
                            kwargs={'specimen_uuid': specimen.uuid}))

    #######
    # GET #
    #######
    if request.method == 'GET':
        if process_type is None:
            context['form_process_type'] = ProcessTypeForm(process_type_choices)
            context['form_process_fields'] = None
        else:
            process_type = request.GET.get('process_type')
            process_fields = get_process_fields(project, process_type)

            form_process_type = ProcessTypeForm(process_type_choices, initial={'process_type': process_type})
            form_process_type.fields['process_type'].widget.attrs['disabled'] = True
            form_process_type.fields['process_type'].widget.attrs['readonly'] = True

            form_process_fields = ProcessFieldsForm(process_fields)
            context['form_process_type'] = form_process_type
            context['form_process_fields'] = form_process_fields
            context['process_type'] = process_type

            context['form_upload_file'] = UploadFileForm()

        if request.is_ajax():
            return render(request, 'ids_projects/processes/get_fields_ajax.html', context)
        else:
            return render(request, 'ids_projects/processes/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        process_type = request.POST.get('process_type')
        process_fields = get_process_fields(project, process_type)

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

                data = {'process_type': process_type}
                data.update(form_process_type.cleaned_data.copy())
                data.update(form_process_fields.cleaned_data.copy())

                # meta data for process
                meta = {'value': data}

                ## Single process registration

                if request.FILES['file'] is None:

                    logger.debug("Single process registration")

                    try:
                        process = Process(api_client=api_client, meta=meta)
                        process.save()

                        if specimen:
                            # create two-way relationship to specimen
                            specimen.add_process(process)
                            specimen.save()
                            process.add_specimen(specimen)
                            process.save()

                        # create two-way relationship to project
                        project.add_process(process)
                        project.save()
                        process.add_project(project)
                        process.save()

                        success_msg = 'Successfully created process.'
                        logger.info(success_msg)
                        messages.success(request, success_msg)
                        return HttpResponseRedirect(
                                    reverse('ids_projects:process-view',
                                            kwargs={'process_uuid': process.uuid}))
                    except HTTPError as e:
                        exception_msg = 'Unable to create new process. %s' % e
                        logger.error(exception_msg)
                        messages.error(request, exception_msg)
                        return HttpResponseRedirect(
                                    reverse('ids_projects:specimen-view',
                                            kwargs={'specimen_uuid': specimen.uuid}))

                ## Bulk ISH process registration
                else:
                    logger.debug("Bulk process registration")

                    try:
                        ISH_meta = _validate_ISH(request.FILES['file'], project)
                        bulk_ISH_registration.apply_async(args=(ISH_meta, meta, project.uuid, request.user.username), serializer='json')

                        return HttpResponseRedirect(
                                    reverse('ids_projects:project-view',
                                            kwargs={'project_uuid': project.uuid}))

                    except Exception as e:
                        traceback.print_exc()
                        exception_msg = repr(e)
                        logger.error(exception_msg)
                        messages.warning(request, exception_msg)

                        return HttpResponseRedirect(
                                        reverse('ids_projects:project-view'),
                                                kwargs={'project_uuid': project_uuid})



def _validate_ISH(f, project):
    ISH_meta = []
    header = True

    reader = csv.reader(f)
    fields = {}

    if header:
        row = next(reader, None)
        for i in range(len(row)):
            fields[row[i]] = i

    for row in reader:
        meta = {}
        for field in fields:
            meta[field] = row[fields[field]]

    ISH_meta.append(meta)
    return ISH_meta


@login_required
@require_http_methods(['GET', 'POST'])
def add_relationship(request, process_uuid):
    """Edit existing process metadata"""

    api_client = request.user.agave_oauth.api_client

    try:
        process = Process(api_client=api_client, uuid=process_uuid)
        project = process.project
        specimen_choices = [(x.uuid, x.title) for x in project.specimens]
        if process.specimen:
            initial = process.specimen.uuid
        else:
            initial = None
    except HTTPError as e:
        logger.error('Error editing process. {}'.format(e.message))
        messages.warning(request, 'Error editing process.')
        return HttpResponseRedirect('/process/{}'.format(process_uuid))
    except Exception as e:
        logger.error('Error editing process. {}'.format(e.message))
        messages.warning(request, 'Process not found.')
        return HttpResponseRedirect('/projects/')

    #######
    # GET #
    #######
    if request.method == 'GET':
        context = {'form_add_relationship': AddRelationshipForm(choices=specimen_choices, initial=initial),
                   'specimen': process.specimen,
                   'project': process.project,
                   'process': process}

        return render(request, 'ids_projects/processes/add_relationship.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':
        form = AddRelationshipForm(specimen_choices, request.POST)

        if form.is_valid():
            try:
                data = form.cleaned_data
                specimen_uuid = data['specimen_choices']
                specimen = Specimen(api_client=api_client, uuid=specimen_uuid)

                process.add_specimen(specimen)
                process.save()

                specimen.add_process(process)
                specimen.save()

                messages.info(request, 'Successfully added relationship.')
                return HttpResponseRedirect(
                    reverse('ids_projects:process-view',
                            kwargs={'process_uuid': process.uuid}))
            except Exception as e:
                exception_msg = 'Unable to add relationship. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                    reverse('ids_projects:process-view',
                            kwargs={'process_uuid': process.uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def edit(request, process_uuid):
    """Edit existing process metadata"""

    api_client = request.user.agave_oauth.api_client

    try:
        process = Process(api_client=api_client, uuid=process_uuid)
        process_type = process.value['process_type']
    except HTTPError as e:
        logger.error('Error editing process. {}'.format(e.message))
        messages.warning(request, 'Error editing process.')
        return HttpResponseRedirect('/process/{}'.format(process_uuid))
    except Exception as e:
        logger.error('Error editing process. {}'.format(e.message))
        messages.warning(request, 'Process not found.')
        return HttpResponseRedirect('/projects/')

    process_fields = get_process_fields(process.project, process_type)

    #######
    # GET #
    #######
    if request.method == 'GET':
        context = {'form_process_edit': ProcessFieldsForm(fields=process_fields, initial=process.value),
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
                process.value.update(form.cleaned_data)
                process.save()

                messages.info(request, 'Process successfully edited.')
                return HttpResponseRedirect(
                            reverse('ids_projects:process-view',
                                    kwargs={'process_uuid': process.uuid}))
            except Exception as e:
                exception_msg = 'Unable to edit process. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:process-view',
                                    kwargs={'process_uuid': process.uuid}))


@login_required
@require_http_methods(['GET'])
def delete(request, process_uuid):
    """Delete a process"""
    next_url = request.GET.get('next_url', None)
    api_client = request.user.agave_oauth.api_client

    try:
        process = Process(api_client=api_client, uuid=process_uuid)

        if next_url is None:
            containers = process.containers
            container = next(iter(containers), None)
            if container:
                name = container.name[6:]
                next_url = reverse('ids_projects:%s-view' % name,
                                   kwargs={'%s_uuid' % name: container.uuid})

        process.delete()

        if next_url is not None:
            return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    except Exception as e:
        exception_msg = 'Unable to load data. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))
