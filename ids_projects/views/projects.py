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


@login_required
def list(request):
    """List all projects"""
    #######
    # GET #
    #######
    if request.method == 'GET':
        context = {'projects':Project().list()}
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

        project = Project(uuid = project_uuid)

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
            project = Project(initial_data = body)

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
            project = Project(uuid = project_uuid)
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
            project = Project(uuid = project_uuid, initial_data = body)
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
def delete(request, project_uuid):
    """Delete a project """
    #######
    # GET #
    #######
    if request.method == 'GET':

        project = Project(uuid = project_uuid)

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
