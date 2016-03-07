from agavepy.agave import Agave, AgaveException
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse,
                         HttpResponseBadRequest,
                         HttpResponseForbidden,
                         HttpResponseNotFound)
from django.shortcuts import render
import json, logging
#from forms import ProjectForm


def _client(request):
    token = request.session.get(getattr(settings, 'AGAVE_TOKEN_SESSION_ID'))
    access_token = token.get('access_token', None)
    url = getattr(settings, 'AGAVE_TENANT_BASEURL')
    return Agave(api_server = url, token = access_token)


def list(request):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':
        a = _client(request)
        query = {'name':'idsvc.project'}
        project_list = a.meta.listMetadata(q=json.dumps(query))

        return render(request, 'ids_projects/index.html', {'data':project_list})

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


def view(request, project_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = _client(request)
        query = {'uuid':project_id}
        project_list = a.meta.listMetadata(q=json.dumps(query))

        print project_list

        try:
            project = project_list[0]
        except:
            return HttpResponseNotFound("Project not found")
        else:
            return HttpResponse(json.dumps(project), content_type="application/json", status=200)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


def create(request):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = _client(request)
        query = {'uuid':project_id}
        project_list = a.meta.listMetadata(q=json.dumps(query))

        print project_list

        try:
            project = project_list[0]
        except:
            return HttpResponseNotFound("Project not found")
        else:
            return HttpResponse(json.dumps(project), content_type="application/json", status=200)

    ########
    # POST #
    ########
    elif request.method == 'POST':
        return HttpResponse("Creating new project: {}".format(len(projects)+1))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


def edit(request, project_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = _client(request)
        query = {'uuid':project_id}
        project_list = a.meta.listMetadata(q=json.dumps(query))

        print project_list

        try:
            project = project_list[0]
        except:
            return HttpResponseNotFound("Project not found")
        else:
            return HttpResponse(json.dumps(project), content_type="application/json", status=200)

    ########
    # POST #
    ########
    elif request.method == 'POST':
        return HttpResponse("Creating new project: {}".format(len(projects)+1))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


def delete(request, project_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = _client(request)
        query = {'uuid':project_id}
        project_list = a.meta.listMetadata(q=json.dumps(query))

        print project_list

        try:
            project = project_list[0]
        except:
            return HttpResponseNotFound("Project not found")
        else:
            return HttpResponse(json.dumps(project), content_type="application/json", status=200)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")
