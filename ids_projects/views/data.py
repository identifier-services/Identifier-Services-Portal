from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import (JsonResponse,
                         HttpResponseRedirect,
                         HttpResponseNotFound)
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import logging, urllib
from ..forms.data import DataTypeForm, SRAForm
from ..models import Project, Specimen, Process, System, Data
from ids.utils import (get_portal_api_client,
                       get_process_type_keys,
                       get_data_fields)

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET'])
def dir_list(request, system_id, file_path=None):
    """"""
    api_client = request.user.agave_oauth.api_client

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

    context = {'process' : data.process,
               'project' : data.project,
               'specimen' : data.specimen,
               'data' : data,
               'process_types' : process_types }

    return render(request, 'ids_projects/data/detail.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def edit(request, data_uuid):
    # TODO: this is not done
    logger.warning('Edit Data not implemented, see Data view.')
    return HttpResponseNotFound()


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

    project_uuid = request.GET.get('project_uuid', None)
    specimen_uuid = request.GET.get('specimen_uuid', None)
    process_uuid = request.GET.get('process_uuid', None)

    api_client = request.user.agave_oauth.api_client

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

    if project is None:
        exception_msg = 'Missing project, cannot create file meta.'
        logger.error(exception_msg)
        raise Exception(exception_msg)

    return project, specimen, process


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

    project, specimen, process = _get_containers(request)

    api_client = request.user.agave_oauth.api_client()

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
                # TODO: creating sra data object is untested with new model
                data = Data(api_client=api_client, sra_id=sra_id)
                data.save()

                _add_to_containers(project, specimen, process, data, relationship)

            except Exception as e:
                exception_msg = 'Unable to access metadata. %s' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:process-view',
                                    kwargs={'process_uuid': process_uuid}))

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
def file_select(request, relationship):
    """"""
    cancel_url = _get_cancel_url(request)

    # if relationship not in ('input', 'output'):
    #     exception_msg = "Invalid relationship type, must be 'input', or 'output'."
    #     logger.error(exception_msg)
    #     messages.warning(request, exception_msg)
    #     return HttpResponseRedirect(cancel_url)

    project, specimen, process = _get_containers(request)

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
            data = Data(api_client=api_client, system_id=system_id, path=file_path)
            data.load_file_info()
        except Exception as e:
            exception_msg = 'Unable to access system with system_id=%s. %s' % (system_id, e)
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(cancel_url)

        try:
            data.save()

            _add_to_containers(project, specimen, process, data, relationship)

        except Exception as e:
            exception_msg = 'Unable to save file info as metadata. %s.' % e
            logger.error(exception_msg)
            messages.error(request, exception_msg)
            return HttpResponseRedirect(cancel_url)

        try:
            result = data.calculate_checksum()
            success_msg = 'Initiated checksum, job id: %s.' % result['id']
            logger.debug(success_msg)
        except Exception as e:
            exception_msg = 'Unable to initiate checksum. %s.' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)

        success_msg = 'Successfully added file to process.'
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

        if next_url is not None:
            return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    except Exception as e:
        exception_msg = 'Unable to load data. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))