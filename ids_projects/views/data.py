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
from ..models import Project, Specimen, Process, System, Data
from helper import client, collapse_meta

logger = logging.getLogger(__name__)


@login_required
def dir_list(request, system_id, file_path=None):
    ########
    # GET #
    ########
    if request.method == 'GET':

        if file_path is None:
            file_path = '/'

        try:
            system = System(system_id=system_id, user=request.user)
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
def file_select(request, relationship):

    process_uuid = request.GET.get('process_uuid', None)

    if relationship not in ('input','output'):
        exception_msg = "Invalid relationship type, must be 'input', or 'output'."
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:process-view',
                            kwargs={'process_uuid': process.uuid}))

    try:
        process = Process(uuid=process_uuid, user=request.user)
    except Exception as e:
        exception_msg = 'Unable to load process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list'))

    #######
    # GET #
    #######
    if request.method == 'GET':

        try:
            system = System(user=request.user)
            systems = system.list()
        except Exception as e:
            exception_msg = 'Unable to load systems. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:process-view',
                                kwargs={'process_uuid': process.uuid}))

        context = {
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
            data = Data(system_id=system_id, path=file_path, user=request.user)
        except Exception as e:
            exception_msg = 'Unable to access system with system_id=%s. %s'\
                            % (system_id, e)
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:process-view',
                                kwargs={'process_uuid': process_uuid}))

        try:
            result = data.save()
        except Exception as e:
            exception_msg = 'Unable to save file info as metadata. %s.' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:process-view',
                                kwargs={'process_uuid': process_uuid}))

        if not 'uuid' in result:
            warning_msg = 'Invalid API response. %s' % result
            logger.warning(warning_msg)
            messages.warning(request, warning_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:process-view',
                                kwargs={'process_uuid': process_uuid}))

        if relationship == 'input':
            process.value['_inputs'].append(result['uuid'])
        else:
            process.value['_outputs'].append(result['uuid'])

        try:
            result = process.save()
        except Exception as e:
            exception_msg = 'Unable to add file to process. %s.' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:process-view',
                                kwargs={'process_uuid': process_uuid}))

        if not 'uuid' in result:
            warning_msg = 'Invalid API response. %s' % result
            logger.warning(warning_msg)
            messages.warning(request, warning_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:process-view',
                                kwargs={'process_uuid': process_uuid}))

        success_msg = 'Successfully added file to process.'
        logger.error(success_msg)
        messages.success(request, success_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:process-view',
                            kwargs={'process_uuid': process_uuid}))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")

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
                return HttpResponseRedirect('/projects/')
        else:
            return HttpResponseRedirect('/projects/')
