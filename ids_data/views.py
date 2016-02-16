from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse,
                         Http404, HttpResponseNotAllowed)
from agavepy.agave import Agave, AgaveException
import json, logging
from forms import DataForm
from forms import SystemForm

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
    except Exception as e:
        parent_id = ''

    a.meta.deleteMetadata(uuid=data_id)

    if json_flag:
        return JsonResponse({'status':'success'})
    else:
        return HttpResponseRedirect('/projects/{}'.format(parent_id))

@login_required
def system(request):
    a = _client(request)
    systems = a.systems.list(type='STORAGE')
    system_choices = []
    for system in systems:

        choice_tuple = (system.id,system.name)
        system_choices.append(choice_tuple)

    if request.method == 'POST':

        form = SystemForm(request.POST, systems=system_choices)

        if form.is_valid():
            choice = form.cleaned_data['system']
            return HttpResponseRedirect('/projects/')
    else:
        return render(request, 'ids_data/system.html',
            {
                'form':SystemForm(systems=system_choices)
            }
        )
