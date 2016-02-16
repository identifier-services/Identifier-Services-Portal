from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse,
                         Http404, HttpResponseNotAllowed)
from agavepy.agave import Agave, AgaveException
import json, logging
from forms import SpecimenForm

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
        specimen_query = {
            'name':'idsvc.specimen',
            'associationIds':'{}'.format(parent_id)
        }
        specimens = a.meta.listMetadata(q=json.dumps(specimen_query))

        if json_flag != False:
            #return JsonResponse(specimens, safe=False)
            return HttpResponse(json.dumps(specimens),
                content_type="application/json", status=200)
        else:
            context = {'specimens':specimens}
            return render(request, 'ids_specimens/index.html', context)
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
        form = SpecimenForm(request.POST)
        if form.is_valid():
            taxon_name = form.cleaned_data['taxon_name']
            specimen_id = form.cleaned_data['specimen_id']
            organ_or_tissue = form.cleaned_data['organ_or_tissue']
            development_stage = form.cleaned_data['development_stage']
            haploid_chromosome_count = form.cleaned_data['haploid_chromosome_count']
            ploidy = form.cleaned_data['ploidy']
            propogation = form.cleaned_data['propogation']
            estimated_genome_size = form.cleaned_data['estimated_genome_size']

            body = {
                "name":"idsvc.specimen",
                "associationIds": parent_id,
                "value": {
                    "taxon_name":taxon_name,
                    "specimen_id":specimen_id,
                    "organ_or_tissue":organ_or_tissue,
                    "development_stage":development_stage,
                    "haploid_chromosome_count":haploid_chromosome_count,
                    "ploidy":ploidy,
                    "propogation":propogation,
                    "estimated_genome_size":estimated_genome_size,
                }
            }
            a = _client(request)
            response = a.meta.addMetadata(body=body)

            if json_flag:
                return JsonResponse(response)
            else:
                return HttpResponseRedirect('/projects/{}'.format(parent_id))

    elif request.method =='GET':
        context = {'form': SpecimenForm()}
        return render(request, 'ids_specimens/create.html', context)

    else:
        message = "Method {} not allowed for this resource".format(request.method)
        if json_flag:
            return JsonResponse({'error':message})
        else:
            raise HttpResponseNotAllowed(message)

def detail(request, specimen_id):
    json_flag=False
    if request.method =='GET':
        a = _client(request)
        specimen = a.meta.getMetadata(uuid=specimen_id)

        if json_flag:
            return JsonResponse(specimen)
        else:
            context = {'specimen':specimen}
            return render(request, 'ids_specimens/index.html', context)
    else:
        message = "Method {} not allowed for this resource".format(request.method)
        if json_flag:
            return JsonResponse({'error':message})
        else:
            raise HttpResponseNotAllowed(message)

@login_required
def edit(request, specimen_id):
    json_flag=False
    if request.method == 'POST':
        pass
    if request.method == 'PUT':
        pass
    elif request.method =='GET':
        context = {'form': SpecimenForm()}
        return render(request, 'ids_specimens/edit.html', context)

    else:
        message = "Method {} not allowed for this resource".format(request.method)
        if json_flag:
            return JsonResponse({'error':message})
        else:
            raise HttpResponseNotAllowed(message)

@login_required
def delete(request, specimen_id):

    json_flag=False
    a = _client(request)

    specimen = a.meta.getMetadata(uuid=specimen_id)
    associationIds = specimen.associationIds

    try:
        parent_id = associationIds[0]
    except Exception as e:
        parent_id = ''

    a.meta.deleteMetadata(uuid=specimen_id)

    if json_flag:
        return JsonResponse({'status':'success'})
    else:
        return HttpResponseRedirect('/projects/{}'.format(parent_id))
    # if request.method == 'POST':
    #     pass
    # if request.method == 'DELETE':
    #     pass
    # elif request.method =='GET':
    #     pass
    # else:
    #     message = "Method {} not allowed for this resource".format(request.method)
    #     if json_flag:
    #         return JsonResponse({'error':message})
    #     else:
    #         raise HttpResponseNotAllowed(message)
