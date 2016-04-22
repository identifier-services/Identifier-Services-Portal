from agavepy.agave import Agave, AgaveException
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import (JsonResponse,
                         HttpResponse,
                         HttpResponseRedirect,
                         HttpResponseBadRequest,
                         HttpResponseForbidden,
                         HttpResponseNotFound,
                         HttpResponseServerError)
from django.shortcuts import render
import json, logging, urllib
from helper import client, collapse_meta


logger = logging.getLogger(__name__)


def _pack_contents(raw):
    contents = []
    for item in raw:
        lm = item.lastModified

        data = {
            'name': item.name,
            'last_modified': lm.strftime('%b %-d %I:%M'),#lm.isoformat(" "),
            'length':item.length,
            'link': item._links['self']['href'],
            'system': item.system,
            'path': item.path,
            'type': item.type,
            'permissions': item.permissions
        }
        choice_tuple = (
            json.dumps(data),
            item.name
        )

        contents.append(choice_tuple)
    return contents


@login_required
def dir_list(request, system_id, file_path=None):
    ########
    # GET #
    ########
    if request.method == 'GET':

        if file_path is None:
            file_path = '/'
        a = client(request)
        try:
            listing = a.files.list(systemId=system_id, filePath=file_path)
            return JsonResponse(listing, safe=False)
        except:
            error_msg = 'The path=%s could not be listed on system=%s. ' \
                        'Please choose another path or system.' % (file_path, system_id)
            return JsonResponse({'message': error_msg}, status=404)


@login_required
def file_select(request):
    #######
    # GET #
    #######
    if request.method == 'GET':
        a = client(request)

        process_uuid = request.GET.get('process_uuid', None)

        context = {
            'process': a.meta.getMetadata(uuid=process_uuid),
            'systems': a.systems.list(type='STORAGE'),
        }

        return render(request, 'ids_projects/data/add_data.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        process_uuid = request.POST.get('process_uuid', None)

        body = urllib.unquote(request.body)
        response_tuples = map(lambda x: (x.split('=')[0],x.split('=')[1]), body.split('&'))
        response = {}
        for key, value in response_tuples:
            response[key] = value

        a = client(request)

        system_id = response['system_id']
        file_path = response['file_path']

        try:
            listing = a.files.list(systemId=system_id, filePath=file_path)
        except:
            error_msg = 'The path=%s could not be listed on system=%s. ' \
                        'Please choose another path or system.' % (file_path, system_id)
            logger.deubg(error_msg)

        process = a.meta.getMetadata(uuid=process_uuid)
        associationIds = process['associationIds']
        associationIds.append(process_uuid)

        for file_info in listing:
            lm = file_info['lastModified']
            data = {
                'name': file_info.name,
                'last_modified': lm.strftime('%b %-d %I:%M'),
                'length':file_info.length,
                'link': file_info._links['self']['href'],
                'system': file_info.system,
                'path': file_info.path,
                'type': file_info.type,
                'permissions': file_info.permissions
            }

            body = {
                "name":"idsvc.data",
                "associationIds": associationIds,
                "value": data
            }

            response = a.meta.addMetadata(body=body)

        return HttpResponseRedirect('/process/{}'.format(process_uuid))

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
