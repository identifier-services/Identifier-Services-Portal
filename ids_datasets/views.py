from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse,
                         Http404, HttpResponseNotAllowed)
from agavepy.agave import Agave, AgaveException
import json, logging
from forms import DatasetForm

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
        dataset_query = {
            'name':'idsvc.dataset',
            'associationIds':'{}'.format(parent_id)
        }
        datasets = a.meta.listMetadata(q=json.dumps(dataset_query))

        if json_flag != False:
            #return JsonResponse(datasets, safe=False)
            return HttpResponse(json.dumps(datasets),
                content_type="application/json", status=200)
        else:
            context = {'datasets':datasets}
            return render(request, 'ids_datasets/index.html', context)
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
        form = DatasetForm(request.POST)
        if form.is_valid():
            process_type = form.cleaned_data['process_type']
            sequence_method = form.cleaned_data['sequence_method']
            sequence_hardware = form.cleaned_data['sequence_hardware']
            reference_sequence = form.cleaned_data['reference_sequence']

            body = {
                "name":"idsvc.dataset",
                "associationIds": parent_id,
                "value": {
                    "process_type":process_type,
                    "sequence_method":sequence_method,
                    "sequence_hardware":sequence_hardware,
                    "reference_sequence":reference_sequence
                }
            }
            a = _client(request)
            response = a.meta.addMetadata(body=body)
            
            if json_flag:
                return JsonResponse(response)
            else:
                return HttpResponseRedirect('/projects/{}'.format(parent_id))

    elif request.method =='GET':
        context = {'form': DatasetForm()}
        return render(request, 'ids_datasets/create.html', context)

    else:
        message = "Method {} not allowed for this resource".format(request.method)
        if json_flag:
            return JsonResponse({'error':message})
        else:
            raise HttpResponseNotAllowed(message)

def detail(request, dataset_id):
    json_flag=False
    if request.method =='GET':
        json_flag = request.GET.get('json', False)

        a = _client(request)
        dataset = a.meta.getMetadata(uuid=dataset_id)

        if json_flag:
            return JsonResponse(dataset)
        else:
            context = {'dataset':dataset}
            return render(request, 'ids_datasets/index.html', context)
    else:
        message = "Method {} not allowed for this resource".format(request.method)
        if json_flag:
            return JsonResponse({'error':message})
        else:
            raise HttpResponseNotAllowed(message)

@login_required
def edit(request, dataset_id):
    json_flag=False
    if request.method == 'POST':
        pass
    if request.method == 'PUT':
        pass
    elif request.method =='GET':
        context = {'form': DatasetForm()}
        return render(request, 'ids_datasets/edit.html', context)

    else:
        message = "Method {} not allowed for this resource".format(request.method)
        if json_flag:
            return JsonResponse({'error':message})
        else:
            raise HttpResponseNotAllowed(message)

@login_required
def delete(request, dataset_id):

    json_flag = request.GET.get('json', False)
    a = _client(request)

    dataset = a.meta.getMetadata(uuid=dataset_id)
    associationIds = dataset.associationIds

    try:
        parent_id = associationIds[0]
    except Exception as e:
        parent_id = ''

    a.meta.deleteMetadata(uuid=dataset_id)

    if json_flag:
        return JsonResponse({'status':'success'})
    else:
        return HttpResponseRedirect('/projects/{}'.format(parent_id))


@login_required
def add_data(request, dataset_id):
    a = _client(request)

    context = {
        'dataset': a.meta.getMetadata(uuid=dataset_id),
        'systems': a.systems.list(type='STORAGE'),
    }

    return render(request, 'ids_datasets/add_data.html', context)
