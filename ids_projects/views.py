from django.conf import settings
from django.shortcuts import render
from forms import ProjectForm

from django.http import HttpResponse, HttpResponseRedirect
from agavepy.agave import Agave, AgaveException

import json

def _client(request):
    token = request.session.get(getattr(settings, 'AGAVE_TOKEN_SESSION_ID'))
    access_token = token.get('access_token', None)
    url = getattr(settings, 'AGAVE_TENANT_BASEURL')
    return Agave(api_server = url, token = access_token)

def index(request):
    token = request.session.get(getattr(settings, 'AGAVE_TOKEN_SESSION_ID'))
    access_token = token.get('access_token', None)
    url = getattr(settings, 'AGAVE_TENANT_BASEURL')

    try:
        a = Agave(api_server = url, token = access_token)
        query = {'name':'idsvc.project'}
        l = a.meta.listMetadata(q=json.dumps(query))
    except AgaveException as e:
        return HttpResponse('{{"error": "{0}" }}'.format(json.dumps(e.message)),
            status = 500, content_type='application/json')
    except Exception as e:
        return HttpResponse('{{"error": "{0}" }}'.format(json.dumps(e.message)),
            status = 500, content_type='application/json')

    return render(request, 'ids_projects/index.html', {'data':l})

def create(request):
    print request
    print request.method
    if request.method == 'POST':
        form = ProjectForm(request.POST)

        title = form.cleaned_data['title']
        inv_type = form.cleaned_data['investigation_type']
        desc = form.cleaned_data['title']

        body = {
            "name":"idsvc.project",
            "value": {
                "title":title,
                "investigation_type":inv_type,
                "description":desc,
            }
        }
        a = _client(request)
        try:
            response = a.meta.addMetadata(body=body)
        except Exception as e:
            print "oops: {}".format(e)
        else:
            print "response: {}".format(response)

        if form.is_valid():
            return HttpResponseRedirect('/projects/')
    # else:
    context = {
        'form': ProjectForm()
    }

    return render(request, 'ids_projects/create.html', context)

def detail(request, uuid):
    a = _client(request)
    query = {'uuid':'{}'.format(uuid)}
    l = a.meta.listMetadata(q=json.dumps(query))[0]
    return render(request, 'ids_projects/detail.html', {'data':l})
