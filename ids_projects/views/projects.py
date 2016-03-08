from agavepy.agave import Agave, AgaveException
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse,
                         HttpResponseRedirect,
                         HttpResponseBadRequest,
                         HttpResponseForbidden,
                         HttpResponseNotFound)
from django.shortcuts import render
import json, logging
from ..forms.projects import ProjectForm


logger = logging.getLogger(__name__)


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

        print '\n\n *** list : {} *** \n\n'.format(project_list)

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

        print '\n\n *** view : {} *** \n\n'.format(project_list)

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
        # import pdb; pdb.set_trace()

        context = {'form': ProjectForm()}
        return render(request, 'ids_projects/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = ProjectForm(request.POST)

        if form.is_valid():

            user_full = request.user.get_full_name()

            title = form.cleaned_data['title']
            inv_type = form.cleaned_data['investigation_type']
            desc = form.cleaned_data['description']

            new_project = {
                'name' : 'idsvc.project',
                'associationIds' : [],
                'value' : {
                    'title' : title,
                    'creator' : user_full,
                    'investigation_type' : inv_type,
                    'description' : desc,
                },
            }

            a = _client(request)
            try:
                response = a.meta.addMetadata(body=new_project)
            except Exception as e:
                logger.debug('Error while attempting to create project metadata: %s' % e)

        return HttpResponseRedirect('/projects/')

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

        print '\n\n *** edit : {} *** \n\n'.format(project_list)

        try:
            project = project_list[0]
        except:
            return HttpResponseNotFound("Project not found")
        else:
            context = {'form': ProjectForm(initial=project)}
            return render(request, 'ids_projects/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = ProjectForm(request.POST)

        if form.is_valid():

            user_full = request.user.get_full_name()

            title = form.cleaned_data['title']
            inv_type = form.cleaned_data['investigation_type']
            desc = form.cleaned_data['description']

            new_project = {
                'name' : 'idsvc.project',
                'associationIds' : [],
                'value' : {
                    'title' : title,
                    'creator' : user_full,
                    'investigation_type' : inv_type,
                    'description' : desc,
                },
            }

            a = _client(request)
            try:
                response = a.meta.updateMetadata(uuid=project_id, body=new_project)
            except Exception as e:
                logger.exception('Error while attempting to edit project metadata.')

        return HttpResponseRedirect('/projects/')

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

        print '\n\n *** delete : {} *** \n\n'.format(project_list)

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
