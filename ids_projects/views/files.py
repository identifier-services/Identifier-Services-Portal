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
from helper import client, collapse_meta


logger = logging.getLogger(__name__)


# {u'mimeType': u'text/directory',
# u'name': u'xwfs',
# u'format': u'folder',
# u'lastModified': datetime.datetime(2013, 9, 26, 11, 24, 8, tzinfo=tzoffset(None, -18000)),
# u'system': u'corral-tacc-00',
# u'length': 4096,
# u'_links': {u'self': {u'href': u'https://agave.iplantc.org/files/v2/media/system/corral-tacc-00//xwfs'},
# u'system': {u'href': u'https://agave.iplantc.org/systems/v2/corral-tacc-00'}},
# u'path': u'/xwfs', u'type': u'dir', u'permissions': u'ALL'}


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
def files_list(request, system_id, file_path=None):
    if file_path is None:
        file_path = '/'
    a = _client(request)
    try:
        listing = a.files.list(systemId=system_id, filePath=file_path)
        return JsonResponse(listing, safe=False)
    except:
        error_msg = 'The path=%s could not be listed on system=%s. ' \
                    'Please choose another path or system.' % (file_path, system_id)
        return JsonResponse({'message': error_msg}, status=404)


@login_required
def create(request, parent_id):
    json_flag = False
    if request.method == 'POST':
        form = DataForm(request.POST)
        if form.is_valid():
            system_id = form.cleaned_data['system_id']
            path = form.cleaned_data['path']

            body = {
                "name":"idsvc.data",
                "associationIds": parent_id,
                "value": {
                    "system_id":system_id,
                    "path":path
                }
            }
            a = _client(request)
            response = a.meta.addMetadata(body=body)

            if json_flag:
                return JsonResponse(response)
            else:
                return HttpResponseRedirect('/projects/{}'.format(parent_id))

    elif request.method =='GET':
        context = {'form': DataForm()}
        return render(request, 'ids_data/create.html', context)

    else:
        message = "Method {} not allowed for this resource".format(request.method)
        if json_flag:
            return JsonResponse({'error':message})
        else:
            raise HttpResponseNotAllowed(message)


@login_required
def add_data(request, process_id):
    a = _client(request)

    context = {
        'dataset': a.meta.getMetadata(uuid=process_id),
        'systems': a.systems.list(type='STORAGE'),
    }

    return render(request, 'ids_datasets/add_data.html', context)


@login_required
def delete(request, data_id):

    json_flag = request.GET.get('json', False)
    a = _client(request)

    data = a.meta.getMetadata(uuid=data_id)
    associationIds = data.associationIds

    try:
        parent_id = associationIds[0]
        parent = a.meta.getMetadata(uuid=parent_id)
    except Exception as e:
        parent_id = ''
        parent = None

    a.meta.deleteMetadata(uuid=data_id)

    if json_flag:
        return JsonResponse({'status':'success'})
    else:
        if parent:
            if parent.name == 'idsvc.project':
                return HttpResponseRedirect('/projects/{}'.format(parent_id))
            elif parent.name == 'idsvc.specimen':
                # return HttpResponseRedirect('/specimens/{}'.format(parent_id))
                return HttpResponseRedirect('/projects/')
            elif parent.name == 'idsvc.dataset':
                # return HttpResponseRedirect('/datasets/{}'.format(parent_id))
                return HttpResponseRedirect('/projects/')
            else:
                return HttpResponseRedirect('/projects/')
        else:
            return HttpResponseRedirect('/projects/')
