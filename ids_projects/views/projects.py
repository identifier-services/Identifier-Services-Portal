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
from django.core.urlresolvers import reverse
from ..forms.projects import ProjectForm
from ..models import Project
from helper import client, collapse_meta
import json, logging


logger = logging.getLogger(__name__)

class User(object):
    def __init__(self, username, agave_oauth):
        self.username = username
        self.agave_oauth = agave_oauth

@login_required
def list(request):
    """List all projects"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        # user = User(request.user.username, request.user.agave_oauth)
        #
        # print user.username

        if request.user.is_authenticated():
            project_list = Project(user=request.user).list()
        else:
            project_list = Project().list()

        if project_list is not None:
            projects = [project.body for project in project_list]
        else:
            projects = None
        context = {'projects':projects,
                   'create_button':True}
        return render(request, 'ids_projects/projects/index.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


def view(request, project_uuid):
    """Queries project metadata and all associated metadata"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        project = Project(uuid = project_uuid, user=request.user)

        context = {'project' : project,
                   'specimen_count' : len(project.specimens),
                   'process_count' : len(project.processes),
                   'file_count' : len(project.data)}

        return render(request, 'ids_projects/projects/detail.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def create(request):
    """Create a new project"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form_project_create': ProjectForm(), 'project': None}
        return render(request, 'ids_projects/projects/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = ProjectForm(request.POST)

        if form.is_valid():

            body = {}
            body['value'] = form.cleaned_data
            user_full = request.user.get_full_name()
            body['value']['creator'] = user_full
            project = Project(initial_data = body, user=request.user)

            result = project.save()

            if 'uuid' in result:
                project_uuid = result['uuid']
                messages.info(request, 'New project created.')
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={'project_uuid': project_uuid}))

        messages.info(request, 'Did not create new project.')
        return HttpResponseRedirect('/projects/')

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def edit(request, project_uuid):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        try:
            project = Project(uuid = project_uuid, user=request.user)
        except:
            logger.error('Error while attempting to edit project, not found.')
            messages.error(request, 'Project not found.')
            return HttpResponseRedirect('/projects/')
        else:
            context = {'form_project_edit': ProjectForm(initial=project.body),
                       'project': project}
            return render(request, 'ids_projects/projects/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = ProjectForm(request.POST)

        if form.is_valid():

            body = {}
            body['value'] = form.cleaned_data
            project = Project(uuid = project_uuid, initial_data = body, user=request.user)
            result = project.save()

            if 'uuid' in result:
                project_uuid = result['uuid']
                messages.info(request, 'Project Successfully edited.')
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={'project_uuid': project_uuid}))

        messages.success(request, 'Did not edit project.')
        return HttpResponseRedirect('/project/{}'.format(project_uuid))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def make_public(request, project_uuid):
    """Make a project public"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        project = Project(uuid = project_uuid, user=request.user)

        # for uuid in project.associationIds:
        #     item = BaseMetadata(uuid = uuid, user=request.user)
        #     item.value['public'] == True
        #     item.save()
        #
        # project.save()
        project.make_public()

        messages.success(request, 'Successfully made project public.')
        return HttpResponseRedirect('/project/%s' % project_uuid)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def make_private(request, project_uuid):
    """Make a project private"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        project = Project(uuid = project_uuid, user=request.user)

        # for uuid in project.associationIds:
        #     item = BaseMetadata(uuid = uuid, user=request.user)
        #     item.value['private'] == True
        #     item.save()
        #
        # project.save()
        project.make_private()

        messages.success(request, 'Successfully made project private.')
        return HttpResponseRedirect('/project/%s' % project_uuid)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def delete(request, project_uuid):
    """Delete a project """
    #######
    # GET #
    #######
    if request.method == 'GET':

        project = Project(uuid = project_uuid, user=request.user)

        for uuid in project.associationIds:
            item = BaseMetadata(uuid = uuid)
            item.delete()

        project.delete()

        messages.success(request, 'Successfully deleted project.')
        return HttpResponseRedirect('/projects/')

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")
