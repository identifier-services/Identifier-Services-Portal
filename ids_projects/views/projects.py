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

        try:
            project = Project(user=request.user)
            public_projects = project.list(public=True)
            private_projects = project.list(public=False)
        except Exception as e:
            exception_msg = 'Unable to load projects. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect('/')

        context = {'public_projects':public_projects,
                   'private_projects':private_projects,
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

        try:
            project = Project(uuid=project_uuid, user=request.user)
        except Exception as e:
            exception_msg = 'Unable to load project. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect('/projects/')

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

            body = { 'value': form.cleaned_data }
            user_full = request.user.get_full_name()
            body['value']['creator'] = user_full

            try:
                project = Project(initial_data=body, user=request.user)
                result = project.save()
            except Exception as e:
                exception_msg = 'Unable to create new project. %s' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)
                return HttpResponseRedirect('/projects/')

            if 'uuid' in result:
                messages.info(request, 'New project created.')
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={'project_uuid': project.uuid}))

        warning_msg = 'Invalid API response. %s' % result
        logger.warning(warning_msg)
        messages.warning(request, warning_msg)
        return HttpResponseRedirect('/projects/')

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def edit(request, project_uuid):
    """ """
    try:
        project = Project(uuid=project_uuid, user=request.user)
    except Exception as e:
        exception_msg = 'Unable to load project. %s' % e
        logger.exception(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/projects/')

    #######
    # GET #
    #######
    if request.method == 'GET':

        context = { 'form_project_edit': ProjectForm(initial=project.body),
                    'project': project }
        return render(request, 'ids_projects/projects/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = ProjectForm(request.POST)

        if form.is_valid():

            try:
                body = { 'value': form.cleaned_data }
                project.set_initial(body)
                result = project.save()
            except Exception as e:
                exception_msg = 'Unable to create new project. %s' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={ 'project_uuid': project.uuid }))

            if 'uuid' in result:
                messages.info(request, 'Project successfully edited.')
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={ 'project_uuid': project.uuid }))

        warning_msg = 'Invalid API response. %s' % result
        logger.warning(warning_msg)
        messages.warning(request, warning_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:project-view',
                            kwargs={ 'project_uuid': project.uuid }))

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

        try:
            project = Project(uuid=project_uuid, user=request.user)
            project.make_public()
        except Exception as e:
            exception_msg = 'Unable to make project and associated objects public.'
            logger.exception(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect('/project/%s' % project_uuid)

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

        try:
            project = Project(uuid=project_uuid, user=request.user)
            project.make_private()
        except Exception as e:
            exception_msg = 'Unable to make project and associated objects public.'
            logger.exception(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect('/project/%s' % project_uuid)

        messages.success(request, 'Successfully made project public.')
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

        try:
            project = Project(uuid=project_uuid, user=request.user)
        except Exception as e:
            exception_msg = 'Unable to load project. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:project-view',
                                kwargs={ 'project_uuid': project.uuid }))

        for uuid in project.associationIds:
            try:
                item = BaseMetadata(uuid=uuid)
            except Exception as e:
                exception_msg = 'Unable to load meta. %s' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)
                # skip the rest of the loop iteration if the item is not found
                continue

            try:
                item.delete()
            except Exception as e:
                exception_msg = 'Unable to delete meta. %s' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)

        try:
            project.delete()
        except Exception as e:
            exception_msg = 'Unable to delete project. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect('/projects/')

        messages.success(request, 'Successfully deleted project.')
        return HttpResponseRedirect('/projects/')

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")
