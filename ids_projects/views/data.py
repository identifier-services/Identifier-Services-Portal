from agavepy.agave import Agave, AgaveException
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import (JsonResponse,
                         HttpResponse,
                         HttpResponseRedirect,
                         HttpResponseBadRequest,
                         HttpResponseForbidden,
                         HttpResponseNotFound,
                         HttpResponseServerError)
from django.shortcuts import render
import json, logging, urllib
from ..forms.data import DataTypeForm, SRAForm
from ..models import Project, Specimen, Process, System, Data
from ids.utils import (get_portal_api_client,
                       get_process_type_keys,
                       get_data_fields)
from helper import client, collapse_meta

logger = logging.getLogger(__name__)


@login_required
def dir_list(request, system_id, file_path=None):
    ########
    # GET #
    ########
    if request.method == 'GET':

        api_client = request.user.agave_oauth.api_client

        if file_path is None:
            file_path = '.'

        try:
            system = System(api_client=api_client, system_id=system_id)
        except:
            exception_msg = 'Unable to access system with system_id=%s.' % system_id
            logger.error(exception_msg)
            return JsonResponse({'message': exception_msg}, status=404)

        try:
            dir_contents = system.listing(file_path)
            return JsonResponse(dir_contents, safe=False)
        except:
            error_msg = 'The path=%s could not be listed on system=%s. ' \
                        'Please choose another path or system.' \
                        % (file_path, system_id)
            return JsonResponse({'message': error_msg}, status=404)

@login_required
def list(request):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        project_uuid = request.GET.get('project_uuid', None)
        specimen_uuid = request.GET.get('specimen_uuid', None)
        process_uuid = request.GET.get('process_uuid', None)

        if request.user.is_anonymous():
            api_client = get_portal_api_client()
        else:
            api_client = request.user.agave_oauth.api_client

        project = None;
        specimen = None;
        process = None;
        datas = None;

        try:
            if project_uuid:
                project = Project(api_client=api_client, uuid=project_uuid)
                datas = project.data
            elif specimen_uuid:
                specimen = Specimen(api_client=api_client, uuid=specimen_uuid)
                datas = specimen.data
                project = specimen.project
            elif process_uuid:
                process = Process(api_client=api_client, uuid=process_uuid)
                datas = process.data
                specimen = process.specimen
                project = process.project
            else:
                datas = Data.list(api_client=api_client)
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

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")

@login_required
def view(request, data_uuid):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        if request.user.is_anonymous():
            api_client = get_portal_api_client()
        else:
            api_client = request.user.agave_oauth.api_client

        try:
            data = Data(api_client=api_client, uuid=data_uuid)
        except Exception as e:
            exception_msg = 'Unable to load data. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

        context = {'process' : data.process,
                   'project' : data.project,
                   'specimen' : data.specimen,
                   'data' : data}

        return render(request, 'ids_projects/data/detail.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")

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

    data_type_choices = [('', 'Choose one'),('SRA', 'SRA'),('File','File')]

    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    #######
    # GET #
    #######
    if request.method == 'GET':

        try:
            if process_uuid is not None:
                process = Process(api_client=api_client, uuid=process_uuid)
                specimen = process.specimen
                project = specimen.project
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
            'form_data_type': form_data_type
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

    return render(request, 'ids_projects/data/type_select.html', context)

@login_required
def add_sra(request, relationship):
    """ """
    project_uuid = request.GET.get('project_uuid', None)
    specimen_uuid = request.GET.get('specimen_uuid', None)
    process_uuid = request.GET.get('process_uuid', None)

    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    try:
        if process_uuid is not None:
            process = Process(api_client=api_client, uuid=process_uuid)
            specimen = process.specimen
            project = specimen.project
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

    #######
    # GET #
    #######
    if request.method == 'GET':

        form_sra_create = SRAForm()

        context = {
            'project': project,
            'specimen': specimen,
            'process': process,
            'form_sra_create': form_sra_create
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
                #TODO: creating sra data object is untested with new model
                data = Data(api_client=api_client, sra_id=sra_id)
            except Exception as e:
                exception_msg = 'Unable to access metadata. %s' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:process-view',
                                    kwargs={'process_uuid': process_uuid}))

            try:
                if process is not None:
                    associationIds = process.associationIds
                    associationIds.append(process.uuid)
                elif specimen is not None:
                    associationIds = specimen.associationIds
                    associationIds.append(specimen.uuid)
                elif project is not None:
                    associationIds = project.associationIds
                    associationIds.append(project.uuid)

                data.associationIds = associationIds
                data.save()
            except Exception as e:
                exception_msg = 'Unable to save sra metadata. %s.' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:process-view',
                                    kwargs={'process_uuid': process_uuid}))

            #TODO: adding data to specimen or project, what do we do?
            if process is not None:
                if relationship == 'input':
                    process.value['_inputs'].append(result['uuid'])
                elif relationship == 'output':
                    process.value['_outputs'].append(result['uuid'])

                try:
                    process.save()
                except Exception as e:
                    exception_msg = 'Unable to add SRA to process. %s.' % e
                    logger.error(exception_msg)
                    messages.error(request, exception_msg)
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
    if process is not None:
        return HttpResponseRedirect(
                    reverse('ids_projects:process-view',
                            kwargs={'process_uuid': process_uuid}))
    elif specimen is not None:
        return HttpResponseRedirect(
                    reverse('ids_projects:specimen-view',
                            kwargs={'specimen_uuid': specimen_uuid}))
    elif project is not None:
        return HttpResponseRedirect(
                    reverse('ids_projects:project-view',
                            kwargs={'project_uuid': project_uuid}))


@login_required
def file_select(request, relationship):

    project_uuid = request.GET.get('project_uuid', None)
    specimen_uuid = request.GET.get('specimen_uuid', None)
    process_uuid = request.GET.get('process_uuid', None)

    api_client = request.user.agave_oauth.api_client

    if relationship not in ('input','output'):
        exception_msg = "Invalid relationship type, must be 'input', or 'output'."
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:process-view',
                            kwargs={'process_uuid': process.uuid}))

    try:
        if process_uuid is not None:
            process = Process(api_client=api_client, uuid=process_uuid)
            specimen = process.specimen
            project = specimen.project
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
            return HttpResponseRedirect(
                        reverse('ids_projects:process-view',
                                kwargs={'process_uuid': process.uuid}))

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
        response_tuples = map(lambda x: (x.split('=')[0],x.split('=')[1]), body.split('&'))
        response = {}
        for key, value in response_tuples:
            response[key] = value

        try:
            system_id = response['system_id']
            file_path = response['file_path']
        except Exception as e:
            exception_msg = 'The post data does not contain sufficient ' \
                            'information to list directory contents.'
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:process-view',
                                kwargs={'process_uuid': process_uuid}))

        try:
            data = Data(api_client=api_client, system_id=system_id, path=file_path)
            data.load_file_info()
        except Exception as e:
            exception_msg = 'Unable to access system with system_id=%s. %s'\
                            % (system_id, e)
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:process-view',
                                kwargs={'process_uuid': process_uuid}))

        try:
            if process is not None:
                associationIds = process.associationIds
                associationIds.append(process.uuid)
            elif specimen is not None:
                associationIds = specimen.associationIds
                associationIds.append(specimen.uuid)
            elif project is not None:
                associationIds = project.associationIds
                associationIds.append(project.uuid)

            data.associationIds = associationIds
            data.save()
        except Exception as e:
            exception_msg = 'Unable to save file info as metadata. %s.' % e
            logger.error(exception_msg)
            messages.error(request, exception_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:process-view',
                                kwargs={'process_uuid': process_uuid}))

        #TODO: what about adding data to specimen or project?
        if process is not None:
            if relationship == 'input':
                process.value['_inputs'].append(data.uuid)
            elif relationship == 'output':
                process.value['_outputs'].append(data.uuid)

            try:
                process.save()
            except Exception as e:
                exception_msg = 'Unable to add file to process. %s.' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
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

        success_msg = 'Successfully added file to process.'
        logger.info(success_msg)
        messages.success(request, success_msg)

        if process is not None:
            return HttpResponseRedirect(
                        reverse('ids_projects:process-view',
                                kwargs={'process_uuid': process_uuid}))
        elif specimen is not None:
            return HttpResponseRedirect(
                        reverse('ids_projects:specimen-view',
                                kwargs={'specimen_uuid': specimen_uuid}))
        elif project is not None:
            return HttpResponseRedirect(
                        reverse('ids_projects:project-view',
                                kwargs={'project_uuid': project_uuid}))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")

@login_required
def do_checksum(request, data_uuid):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        try:
            data = Data(uuid=data_uuid, user=request.user)
        except Exception as e:
            exception_msg = 'Unable to load data. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

        try:
            data.calculate_checksum()
        except Exception as e:
            exception_msg = 'Unable to initiate checksum. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:data-view',
                                kwargs={'data_uuid': data.uuid}))

        sucess_msg = 'Initiated checksum job.'
        logger.info(sucess_msg)
        messages.success(request, sucess_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:data-view',
                            kwargs={'data_uuid': data.uuid}))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")

@login_required
def request_id(request, data_uuid, id_type):
    pass

@login_required
def data_delete(request, data_uuid):

    json_flag = request.GET.get('json', False)
    a = client(request)

    data = a.meta.getMetadata(uuid=data_uuid)
    associationIds = data.associationIds

    # TODO: this is dumb, but about to get replaced anyway
    try:
        parent_id = associationIds[0]
        parent = a.meta.getMetadata(uuid=parent_id)
    except Exception as e:
        parent_id = ''
        parent = None

    a.meta.deleteMetadata(uuid=data_uuid)

    if json_flag:
        return JsonResponse({'status':'success'})
    else:
        if parent:
            if parent.name == 'idsvc.project':
                return HttpResponseRedirect('/project/{}'.format(parent_id))
            elif parent.name == 'idsvc.specimen':
                return HttpResponseRedirect('/specimen/{}'.format(parent_id))
            elif parent.name == 'idsvc.process':
                return HttpResponseRedirect('/process/{}'.format(parent_id))
            else:
                return HttpResponseRedirect('/projects/private/')
        else:
            return HttpResponseRedirect('/projects/private/')
