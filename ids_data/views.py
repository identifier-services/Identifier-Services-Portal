from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse,
                         Http404, HttpResponseNotAllowed)

from agavepy.agave import Agave, AgaveException
import json, logging, urllib
from forms import DirectoryForm

import datetime

logger = logging.getLogger(__name__)

from django.shortcuts import render

def _client(request):
    token = request.session.get(getattr(settings, 'AGAVE_TOKEN_SESSION_ID'))
    access_token = token.get('access_token', None)
    url = getattr(settings, 'AGAVE_TENANT_BASEURL')
    return Agave(api_server = url, token = access_token)

def index(request, parent_id=''):
    if request.method == 'GET':

        json_flag = request.GET.get('json', False)

        a = _client(request)
        data_query = {
            'name':'idsvc.data',
            'associationIds':'{}'.format(parent_id)
        }
        datas = a.meta.listMetadata(q=json.dumps(data_query))

        if json_flag != False:
            #return JsonResponse(datas, safe=False)
            return HttpResponse(json.dumps(datas),
                content_type="application/json", status=200)
        else:
            context = {'datas':datas}

            return render(request, 'ids_data/index.html', context)
    else:
        message = "Method {} not allowed for this resource".format(request.method)
        if json_flag:
            return JsonResponse({'error':message})
        else:
            raise HttpResponseNotAllowed(message)

def _pack_contents(raw):

# {u'mimeType': u'text/directory',
# u'name': u'xwfs',
# u'format': u'folder',
# u'lastModified': datetime.datetime(2013, 9, 26, 11, 24, 8, tzinfo=tzoffset(None, -18000)),
# u'system': u'corral-tacc-00',
# u'length': 4096,
# u'_links': {u'self': {u'href': u'https://agave.iplantc.org/files/v2/media/system/corral-tacc-00//xwfs'},
# u'system': {u'href': u'https://agave.iplantc.org/systems/v2/corral-tacc-00'}},
# u'path': u'/xwfs', u'type': u'dir', u'permissions': u'ALL'}

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

def list(request, parent_id, system_id):
    a = _client(request)

    if request.method == 'GET':
        path = urllib.unquote(request.GET.get('path', "."))

        if path != '.':
            last_slash = path.rfind('/')
            if last_slash > 0:
                ancestor = path[:last_slash]
            else:
                ancestor = "."
        else:
            ancestor = None

        logger.debug("GET request path: {}".format(path))

        raw_contents = a.files.list(systemId=system_id, filePath=path)
        contents = _pack_contents(raw_contents)

        try:
            parent = a.meta.listMetadata(uuid=parent_id)[0]
            if parent.name == 'idsvc.dataset':
                process_type == parent.value.process_type
            else:
                process_type = None
        except:
            parent = None
            process_type = None

        in_type = None
        out_type = None

        if process_type:
            if process_type == 'Sequencing':
                in_type = "?"
                out_type = ".fq"
            elif process_type == 'Alignment':
                in_type = ".fq"
                out_type = ".bam"
            elif process_type == 'Anlysis':
                in_type = ".bam"
                out_type = "bp."

        # will use this to construct the form when handling the post
        request.session['dir_contents'] = contents

        return render(request, 'ids_data/index.html',
            {
                'form':DirectoryForm(contents=contents),
                'system_id':system_id,
                'path':path,
                'ancestor':ancestor,
                'in_type':int_type,
                'out_type':out_type
            }
        )

    elif request.method == 'POST':
        path = urllib.unquote(request.POST.get('path', "."))

        logger.debug("POST request path: {}".format(path))

        contents = request.session.get('dir_contents')
        if not contents:
            raw_contents = a.files.list(systemId=system_id, filePath=path)
            contents = _pack_contents(raw_contents)

        form = DirectoryForm(request.POST, contents=contents)

        if form.is_valid():
            choice = form.cleaned_data['contents']

            logger.debug("form valid, choice: {}".format(choice))
            system = json.loads(choice)

            if system['type'] == 'dir':
                path = urllib.quote(system['path'], safe='')
                url = '/data/{}/{}/list/?path={}'.format(
                    parent_id, system_id, path
                )
                return HttpResponseRedirect(url)
            else:
                choice = json.loads(choice)

                body = {
                    "name":"idsvc.data",
                    "associationIds": parent_id,
                    "value": {
                        'name': choice['name'],
                        'last_modified': choice['last_modified'],
                        'length': choice['length'],
                        'link': choice['link'],
                        'system': choice['system'],
                        'path': choice['path'],
                        'type': choice['type'],
                        'permissions': choice['permissions']
                    }
                }
                response = a.meta.addMetadata(body=body)

                return HttpResponseRedirect('/projects/')

    else:

        raise HttpResponseNotAllowed(message)

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

def detail(request, data_id):
    json_flag=False
    if request.method =='GET':
        json_flag = request.GET.get('json', False)

        a = _client(request)
        data = a.meta.getMetadata(uuid=data_id)

        if json_flag:
            return JsonResponse(data)
        else:
            context = {'data':data}
            return render(request, 'ids_data/index.html', context)
    else:
        message = "Method {} not allowed for this resource".format(request.method)
        if json_flag:
            return JsonResponse({'error':message})
        else:
            raise HttpResponseNotAllowed(message)

@login_required
def edit(request, data_id):
    json_flag=False
    if request.method == 'POST':
        pass
    if request.method == 'PUT':
        pass
    elif request.method =='GET':
        context = {'form': DataForm()}
        return render(request, 'ids_data/edit.html', context)

    else:
        message = "Method {} not allowed for this resource".format(request.method)
        if json_flag:
            return JsonResponse({'error':message})
        else:
            raise HttpResponseNotAllowed(message)

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
                #return HttpResponseRedirect('/specimens/{}'.format(parent_id))
                return HttpResponseRedirect('/projects/')
            elif parent.name == 'idsvc.dataset':
                #return HttpResponseRedirect('/datasets/{}'.format(parent_id))
                return HttpResponseRedirect('/projects/')
            else:
                return HttpResponseRedirect('/projects/')
        else:
            return HttpResponseRedirect('/projects/')
