from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import (JsonResponse,
                         HttpResponseRedirect,
                         HttpResponseNotFound)
from requests.exceptions import HTTPError
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from ..forms.data import DataTypeForm, SRAForm, DataForm, AddRelationshipForm
from ..models import Project, Specimen, Process, System, Data
from ids.utils import (get_portal_api_client,
                       get_process_type_keys,
                       get_data_fields)

from ..forms.upload_option import UploadOptionForm, UploadFileForm
from ids_projects.tasks import bulk_images_registration

import traceback
import csv
import logging
import urllib
import json
import re
import requests

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET'])
def dir_list(request, system_id, file_path=None):
    """"""
    api_client = request.user.agave_oauth.api_client

    logger.debug('List contents of dir: %s, on system: %s' % (system_id, file_path))

    if file_path is None:
        file_path = '.'

    try:
        system = System(api_client=api_client, system_id=system_id)
    except Exception as e:
        exception_msg = 'Unable to access system with system_id=%s. %s' % (system_id, e)
        logger.error(exception_msg)
        return JsonResponse({'message': exception_msg}, status=404)

    try:
        dir_contents = system.listing(file_path)
        return JsonResponse(dir_contents, safe=False)
    except Exception as e:
        error_msg = 'The path=%s could not be listed on system=%s. ' \
                    'Please choose another path or system. %s' \
                    % (file_path, system_id, e)
        return JsonResponse({'message': error_msg}, status=404)


@login_required
@require_http_methods(['GET'])
def list(request):
    """ """
    project_uuid = request.GET.get('project_uuid', None)
    specimen_uuid = request.GET.get('specimen_uuid', None)
    process_uuid = request.GET.get('process_uuid', None)

    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    project = None
    specimen = None
    process = None
    data = None

    try:
        if project_uuid:
            project = Project(api_client=api_client, uuid=project_uuid)
            data = project.data
        elif specimen_uuid:
            specimen = Specimen(api_client=api_client, uuid=specimen_uuid)
            data = specimen.data
            project = specimen.project
        elif process_uuid:
            process = Process(api_client=api_client, uuid=process_uuid)
            data = process.data
            specimen = process.specimen
            project = process.project
        else:
            data = Data.list(api_client=api_client)
    except Exception as e:
        exception_msg = 'Unable to load data. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    context = { 'project' : project,
                'specimen': specimen,
                'process' : process,
                'data'    : data }

    return render(request, 'ids_projects/data/index.html', context)


@login_required
@require_http_methods(['GET'])
def view(request, data_uuid):
    """ """
    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    try:
        data = Data(api_client=api_client, uuid=data_uuid)
        project = data.project
    except Exception as e:
        exception_msg = 'Unable to load data. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        process_types = get_process_type_keys(project)
        data_fields = get_data_fields(project)
        data.set_fields(data_fields)
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)

    context = {'process': data.process,
               'project': data.project,
               'specimen': data.specimen,
               'data': data,
               'process_types': process_types}

    return render(request, 'ids_projects/data/detail.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def add_relationship(request, data_uuid):
    """Edit existing process metadata"""

    api_client = request.user.agave_oauth.api_client

    try:
        data = Data(api_client=api_client, uuid=data_uuid)
        project = data.project
        process_choices = [(x.uuid, x.title) for x in project.processes]
        if data.process:
            initial = data.process.uuid
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
        context = {'form_add_relationship': AddRelationshipForm(choices=process_choices, initial=initial),
                   'process': data.process,
                   'specimen': data.specimen,
                   'project': data.project,
                   'data': data}

        return render(request, 'ids_projects/data/add_relationship.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':
        form = AddRelationshipForm(process_choices, request.POST)

        if form.is_valid():
            try:
                cleaned_data = form.cleaned_data
                process_uuid = cleaned_data['specimen_choices']
                input_output = cleaned_data['input_output']
                process = Process(api_client=api_client, uuid=process_uuid)

                if input_output == 'input':
                    process.add_input(data)
                    data.add_is_input_to(process)
                elif input_output == 'output':
                    process.add_output(data)
                    data.add_is_output_of(process)

                process.save()
                data.save()

                messages.info(request, 'Successfully added relationship.')
                return HttpResponseRedirect(
                    reverse('ids_projects:process-view',
                            kwargs={'process_uuid': data.uuid}))
            except Exception as e:
                exception_msg = 'Unable to add relationship. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                    reverse('ids_projects:process-view',
                            kwargs={'process_uuid': data.uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def edit(request, data_uuid):
    """"""
    api_client = request.user.agave_oauth.api_client

    try:
        data = Data(api_client=api_client, uuid=data_uuid)
        project = data.project
    except Exception as e:
        exception_msg = 'Unable to edit data. %s' % e
        logger.exception(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/projects/')

    try:
        data_fields = get_data_fields(project)
    except Exception as e:
        exception_msg = 'Missing project type information, cannot edit data. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
            reverse('ids_projects:project-view',
                    kwargs={'project_uuid': project.uuid}))

    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form_data_edit': DataForm(fields=data_fields, initial=data.value),
                   'data': data,
                   'project': data.project}

        return render(request, 'ids_projects/data/edit.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = DataForm(data_fields, request.POST)

        if form.is_valid():

            try:
                data.value.update(form.cleaned_data)
                data.save()

                messages.info(request, 'Data successfully edited.')
                return HttpResponseRedirect(
                    reverse('ids_projects:data-view',
                            kwargs={'data_uuid': data.uuid}))
            except Exception as e:
                exception_msg = 'Unable to edit data. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                    reverse('ids_projects:data-view',
                            kwargs={'data_uuid': data.uuid}))


def _get_cancel_url(request):
    """"Internal method..."""
    project_uuid = request.GET.get('project_uuid', None)
    specimen_uuid = request.GET.get('specimen_uuid', None)
    process_uuid = request.GET.get('process_uuid', None)

    if process_uuid is not None:
        viewname = 'ids_projects:process-view'
        args = (process_uuid,)
    elif specimen_uuid is not None:
        viewname = 'ids_projects:specimen-view'
        args = (specimen_uuid,)
    elif project_uuid is not None:
        viewname = 'ids_projects:project-view'
        args = (project_uuid,)
    else:
        viewname = 'ids_projects:project-list-private'
        args = None

    return reverse(viewname, args=args)


@login_required
@require_http_methods(['GET', 'POST'])
def type_select(request):
    """ """
    project_uuid = request.GET.get('project_uuid', None)
    specimen_uuid = request.GET.get('specimen_uuid', None)
    process_uuid = request.GET.get('process_uuid', None)
    relationship = request.GET.get('relationship', None)

    # check to make sure we have at least one parent uuid (project or specimen)

    if not process_uuid and not specimen_uuid and not project_uuid:
        messages.warning(request, 'Missing parent UUID, cannot add data.')
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    data_type_choices = [('', 'Choose one'), ('SRA', 'SRA'), ('File','File')]

    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    #######
    # GET #
    #######
    if request.method == 'GET':
        project = None
        specimen = None
        process = None
        try:
            if process_uuid is not None:
                process = Process(api_client=api_client, uuid=process_uuid)
                specimen = process.specimen
                project = process.project
            elif specimen_uuid is not None:
                process = None
                specimen = Specimen(api_client=api_client, uuid=specimen_uuid)
                project = specimen.project
            elif project_uuid is not None:
                process = None
                specimen = None
                project = Project(api_client=api_client, uuid=project_uuid)
        except Exception as e:
            exception_msg = 'Unable to load parent object. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

        form_data_type = DataTypeForm(data_type_choices)

        context = {
            'project': project,
            'specimen': specimen,
            'process': process,
            'form_data_type': form_data_type,
            'cancel_url': _get_cancel_url(request)
        }

        return render(request, 'ids_projects/data/type_select.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form_data_type = DataTypeForm(data_type_choices, request.POST)

        if form_data_type.is_valid():

            data = form_data_type.cleaned_data
            data_type = data.get('data_type')

            if data_type == 'SRA':
                if process_uuid is not None:
                    return HttpResponseRedirect('%s?process_uuid=%s' %
                        (reverse('ids_projects:add-sra', kwargs={'relationship': relationship}), process_uuid)
                    )
                elif specimen_uuid is not None:
                    return HttpResponseRedirect('%s?specimen_uuid=%s' %
                        (reverse('ids_projects:add-sra', kwargs={'relationship': relationship}), specimen_uuid)
                    )
                elif project_uuid is not None:
                    return HttpResponseRedirect('%s?project_uuid=%s' %
                        (reverse('ids_projects:add-sra', kwargs={'relationship': relationship}), project_uuid)
                    )

            elif data_type == 'File':
                if process_uuid is not None:
                    return HttpResponseRedirect('%s?process_uuid=%s' %
                        (reverse('ids_projects:file-select', kwargs={'relationship': relationship}), process_uuid)
                    )
                elif specimen_uuid is not None:
                    return HttpResponseRedirect('%s?specimen_uuid=%s' %
                        (reverse('ids_projects:file-select', kwargs={'relationship': relationship}), specimen_uuid)
                    )
                elif project_uuid is not None:
                    return HttpResponseRedirect('%s?project_uuid=%s' %
                        (reverse('ids_projects:file-select', kwargs={'relationship': relationship}), project_uuid)
                    )


def _get_containers(request):
    """Internal method..."""

    if not request.GET:
        return None, None, None, None

    project_uuid = request.GET.get('project_uuid', None)
    specimen_uuid = request.GET.get('specimen_uuid', None)
    process_uuid = request.GET.get('process_uuid', None)
    data_uuid = request.GET.get('data_uuid', None)

    api_client = request.user.agave_oauth.api_client

    if data_uuid is not None:
        data = Data(api_client=api_client, uuid=data_uuid)
        process = data.process
        specimen = data.specimen
        project = data.project
    if process_uuid is not None:
        data = None
        process = Process(api_client=api_client, uuid=process_uuid)
        specimen = process.specimen
        project = process.project
    elif specimen_uuid is not None:
        data = None
        process = None
        specimen = Specimen(api_client=api_client, uuid=specimen_uuid)
        project = specimen.project
    elif project_uuid is not None:
        data = None
        process = None
        specimen = None
        project = Project(api_client=api_client, uuid=project_uuid)

    if project is None:
        exception_msg = 'Missing project, cannot create file meta.'
        logger.error(exception_msg)
        raise Exception(exception_msg)

    return project, specimen, process, data


def _add_to_containers(project, specimen, process, data, relationship):
    """Internal method..."""

    if process is not None:
        # create two-way relationship to process

        if relationship == 'input':
            process.add_input(data)
            process.save()
            data.add_is_input_to(process)
            data.save()

        elif relationship == 'output':
            process.add_output(data)
            process.save()
            data.add_is_output_of(process)
            data.save()

    if specimen is not None:
        # create two-way relationship to specimen
        specimen.add_part(data)
        specimen.save()
        data.add_container(specimen)
        data.save()

    if project is not None:
        # create two-way relationship to project
        project.add_part(data)
        project.save()
        data.add_container(project)
        data.save()


@login_required
@require_http_methods(['GET', 'POST'])
def add_sra(request, relationship):
    """ """
    cancel_url = _get_cancel_url(request)

    # if relationship not in ('input', 'output'):
    #     exception_msg = "Invalid relationship type, must be 'input', or 'output'."
    #     logger.error(exception_msg)
    #     messages.warning(request, exception_msg)
    #     return HttpResponseRedirect(cancel_url)

    project, specimen, process, data = _get_containers(request)

    api_client = request.user.agave_oauth.api_client

    #######
    # GET #
    #######
    if request.method == 'GET':

        form_sra_create = SRAForm()

        context = {
            'project': project,
            'specimen': specimen,
            'process': process,
            'form_sra_create': form_sra_create,
            'cancel_url': cancel_url
        }

        return render(request, 'ids_projects/data/add_sra.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form_sra_create = SRAForm(request.POST)

        if form_sra_create.is_valid():

            body = form_sra_create.cleaned_data
            sra_id = body.get('sra_id')

            try:
                if not data:
                    data = Data(api_client=api_client, sra_id=sra_id)
                    data.save()
                    _add_to_containers(project, specimen, process, data, relationship)
                else:
                    data.sra_id = sra_id
                    # TODO: this should happen in the model
                    data.value.update({'sra_id': sra_id})
                    data.save()
            except Exception as e:
                exception_msg = 'Unable to access metadata. %s' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)
                return HttpResponseRedirect(cancel_url)

            try:
                result = data.calculate_checksum()
                success_msg = 'Initiated checksum, job id: %s.' % result['id']
                logger.debug(success_msg)
            except Exception as e:
                exception_msg = 'Unable to initiate checksum. %s.' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)

    success_msg = "SRA successfully added."
    logger.info(success_msg)
    messages.success(request, success_msg)
    return HttpResponseRedirect(
        reverse('ids_projects:data-view',
                kwargs={'data_uuid': data.uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def add_images(request):
    print "In the add images"
    project_uuid = request.GET.get('project_uuid', False)

    if not project_uuid:
        messages.warning(request, 'Missing project UUID, cannot create specimen.')
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    project = Project(api_client=api_client, uuid=project_uuid)

    if request.method == 'POST':

        if request.FILES['file'] != None:
            try:
                images_meta = _image_process(request.FILES['file'], project)
                bulk_images_registration.apply_async(args=(images_meta, project_uuid, request.user.username), serilizer = 'json')
                return HttpResponseRedirect(
                                    reverse('ids_projects:project-view',
                                            kwargs={'project_uuid': project.uuid}))


            except Exception as e:
                traceback.print_exc()
                exception_msg = repr(e)
                logger.error(exception_msg)
                messages.warning(request, exception_msg)

                return HttpResponseRedirect(
                                    reverse('ids_projects:project-view',
                                            kwargs={'project_uuid': project.uuid}))

    # GET
    else:
        print "GET request"
        context = {'project': project}
        context['form_upload_file'] = UploadFileForm()
        return render(request, 'ids_projects/data/add_images.html', context)

def _image_process(f, project):
    header = True
    reader = csv.reader(f)
    fields = get_data_fields(project)
    images_meta = []

    if header:
        next(reader, None)

    for row in reader:
        meta = {}
        # for field in fields:
        #     meta[field['id']] = None

        image_url = row[0]
        data_url = re.sub(r'image_service', "data_service", image_url)
        xmlString = _get_image_meta_by_url(data_url)

        meta['image_uri'] = image_url
        meta['data_uri'] = data_url

        match = re.search(r'.* name=\"(.*)\" owner.*', xmlString, re.I)
        if match:
            meta['name'] = match.group(1)

        images_meta.append(meta)

    return images_meta

def _get_image_meta_by_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

@login_required
@require_http_methods(['GET', 'POST'])
def file_select(request, relationship):
    """"""
    cancel_url = _get_cancel_url(request)

    # if relationship not in ('input', 'output'):
    #     exception_msg = "Invalid relationship type, must be 'input', or 'output'."
    #     logger.error(exception_msg)
    #     messages.warning(request, exception_msg)
    #     return HttpResponseRedirect(cancel_url)

    project, specimen, process, data = _get_containers(request)

    api_client = request.user.agave_oauth.api_client

    #######
    # GET #
    #######
    if request.method == 'GET':

        try:
            systems = System.list(api_client=api_client, system_type="STORAGE")
        except Exception as e:
            exception_msg = 'Unable to load systems. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(cancel_url)

        context = {
            'project': project,
            'specimen': specimen,
            'process': process,
            'systems': systems,
        }

        return render(request, 'ids_projects/data/select_files.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        body = urllib.unquote(request.body)
        response_tuples = map(lambda x: (x.split('=')[0], x.split('=')[1]), body.split('&'))
        response = {}
        for key, value in response_tuples:
            response[key] = value

        try:
            system_id = response['system_id']
            file_path = response['file_path']
        except Exception as e:
            exception_msg = 'The post data does not contain sufficient ' \
                            'information to list directory contents. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(cancel_url)

        try:
            if not data:
                data = Data(api_client=api_client, system_id=system_id, path=file_path)
                data.load_file_info()
                data.save()
                _add_to_containers(project, specimen, process, data, relationship)
            else:
                data.system_id = system_id
                # TODO: this should happen in the model
                data.value.update({'system_id': system_id})
                data.path = file_path
                # TODO: this should happen in the model
                data.value.update({'path': file_path})
                data.load_file_info()
                data.save()

        except Exception as e:
            exception_msg = 'Unable to access system with system_id=%s. %s' % (system_id, e)
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(cancel_url)

        # if relationship != 'identical':
        #     try:
        #         data.save()
        #
        #         _add_to_containers(project, specimen, process, data, relationship)
        #
        #     except Exception as e:
        #         exception_msg = 'Unable to save file info as metadata. %s.' % e
        #         logger.error(exception_msg)
        #         messages.error(request, exception_msg)
        #         return HttpResponseRedirect(cancel_url)

        try:
            result = data.calculate_checksum()
            success_msg = 'Initiated checksum, job id: %s.' % result['id']
            logger.debug(success_msg)
        except Exception as e:
            exception_msg = 'Unable to initiate checksum. %s.' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)

        success_msg = 'Successfully added file.'
        logger.info(success_msg)
        messages.success(request, success_msg)

        return HttpResponseRedirect(
                    reverse('ids_projects:data-view',
                            kwargs={'data_uuid': data.uuid}))


@login_required
@require_http_methods(['GET'])
def do_checksum(request, data_uuid):
    """ """
    api_client = request.user.agave_oauth.api_client

    try:
        data = Data(api_client=api_client, uuid=data_uuid)
    except Exception as e:
        exception_msg = 'Unable to load data. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        data.calculate_checksum()

        success_msg = 'Initiated checksum job.'
        logger.info(success_msg)
        messages.success(request, success_msg)
        return HttpResponseRedirect(
            reverse('ids_projects:data-view',
                    kwargs={'data_uuid': data.uuid}))
    except Exception as e:
        exception_msg = 'Unable to initiate checksum. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:data-view',
                            kwargs={'data_uuid': data.uuid}))


@login_required
@require_http_methods(['GET'])
def request_id(request, data_uuid, id_type):
    # TODO: this is not done
    logger.warning('Request ID not implemented, see Data view.')
    return HttpResponseNotFound()


@login_required
@require_http_methods(['GET'])
def data_delete(request, data_uuid):
    """ """
    next_url = request.GET.get('next_url', None)
    api_client = request.user.agave_oauth.api_client

    try:
        data = Data(api_client=api_client, uuid=data_uuid)

        if next_url is None:
            containers = data.containers
            container = next(iter(containers), None)
            if container:
                name = container.name[6:]
                next_url = reverse('ids_projects:%s-view' % name,
                                   kwargs={'%s_uuid' % name: container.uuid})

        data.delete()

        success_msg = 'Successfully unregistered data.'
        logger.info(success_msg)
        messages.success(request, success_msg)

        if next_url is not None:
            return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    except Exception as e:
        exception_msg = 'Unable to load data. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))
