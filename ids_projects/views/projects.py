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
from ..forms.projects import ProjectForm
from ..models import Project
from helper import client, collapse_meta


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
                   'file_count' : 1}#len(project.files)}

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

        context = {'form': ProjectForm(), 'project': None}
        return render(request, 'ids_projects/projects/create.html', context)

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

            a = client(request)

            try:
                response = a.meta.addMetadata(body=new_project)
            except Exception as e:
                logger.debug('Error while attempting to create project metadata: %s' % e)
            else:
                messages.success(request, 'Successfully created project.')
                return HttpResponseRedirect('/project/{}'.format(response['uuid']))

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

        a = client(request)
        try:
            project_raw = a.meta.getMetadata(uuid=project_uuid)
            project = collapse_meta(project_raw)
        except:
            logger.error('Error while attempting to edit project, not found.')
            messages.error(request, 'Project not found.')
            return HttpResponseRedirect('/projects/')
        else:
            context = {'form': ProjectForm(initial=project),
                       'project': project}
            return render(request, 'ids_projects/projects/create.html', context)

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

            a = client(request)
            try:
                response = a.meta.updateMetadata(uuid=project_uuid, body=new_project)
            except Exception as e:
                logger.error('Error while attempting to edit project metadata.')
                messages.error(request, 'Error while attempting to edit specimen.')
                return HttpResponseRedirect('/projects/')
            else:
                messages.success(request, 'Successfully edited project.')
                return HttpResponseRedirect('/project/{}'.format(project_uuid))

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

        # TODO: ask user if they want to delete associated objects?

        a = client(request)

        # find all associated objects
        query = {'associationIds':'{}'.format(project_uuid)}
        results = a.meta.listMetadata(q=json.dumps(query))

        # delete all associated objects
        for result in results:
            a.meta.deleteMetadata(uuid=result.uuid)

        # delete project
        try:
            a.meta.deleteMetadata(uuid=project_uuid)
        except:
            logger.error('Error deleting project. {}'.format(e.message) )
            messages.error(request, 'Project deletion unsuccessful.')

            return HttpResponseRedirect('/projects/')
        else:
            messages.success(request, 'Successfully deleted project.')
            return HttpResponseRedirect('/projects/')

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")
