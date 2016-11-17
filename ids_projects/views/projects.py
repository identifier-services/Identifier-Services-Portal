from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from ids.utils import (get_portal_api_client,
                       get_process_type_keys,
                       get_project_form_fields,
                       get_investigation_type)
from ..forms.projects import ProjectForm
from ..models.project import Project
import logging

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET'])
def list_private(request):
    """List private projects"""
    api_client = request.user.agave_oauth.api_client

    try:
        projects = Project.list(api_client=api_client)
    except Exception as e:
        exception_msg = 'Unable to load projects. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/')

    context = { 'type': 'private', 'private_projects': projects, 'create_button': True }

    return render(request, 'ids_projects/projects/index.html', context)


@login_required
@require_http_methods(['GET'])
def view(request, project_uuid):
    """Queries project metadata and all associated metadata"""
    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        # api_client = get_portal_api_client()
        api_client = request.user.agave_oauth.api_client

    try:
        project = Project(api_client=api_client, uuid=project_uuid)
    except Exception as e:
        exception_msg = 'Unable to load project. %s' % e
        logger.error(exception_msg)
        messages.error(request, exception_msg)
        return HttpResponseRedirect('/projects/')

    try:
        process_types = get_process_type_keys(project)
        project_fields = get_project_form_fields()
        project.set_fields(project_fields)
        investigation_type = get_investigation_type(project)

        context = {'project': project,
                   'investigation_type': investigation_type,
                   'process_types': process_types}

        return render(request, 'ids_projects/projects/detail.html', context)
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:project-list-private'))


@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    """Create a new project"""
    api_client = request.user.agave_oauth.api_client

    try:
        project_fields = get_project_form_fields()
    except Exception as e:
        exception_msg = 'Unable to load config values, cannot create project. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:project-list-private'))

    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form_project_create': ProjectForm(project_fields), 'project': None}
        return render(request, 'ids_projects/projects/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = ProjectForm(project_fields, request.POST)

        if form.is_valid():

            body = form.cleaned_data
            user_full = request.user.get_full_name()
            body.update({'creator': user_full})

            try:
                project = Project(api_client=api_client, value=body)
                project.save()

                messages.info(request, 'New project created.')
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={'project_uuid': project.uuid}))
            except Exception as e:
                exception_msg = 'Unable to create new project. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect('/projects/')


@login_required
@require_http_methods(['GET', 'POST'])
def edit(request, project_uuid):
    """Edit a project, given the uuid"""
    api_client = request.user.agave_oauth.api_client

    try:
        project_fields = get_project_form_fields()
    except Exception as e:
        exception_msg = 'Unable to load config values, cannot create project. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:project-list-private'))

    try:
        project = Project(api_client=api_client, uuid=project_uuid)
    except Exception as e:
        exception_msg = 'Unable to load project. %s' % e
        logger.exception(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/projects/')

    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form_project_edit': ProjectForm(fields=project_fields, initial=project.value),
                   'project': project}
        return render(request, 'ids_projects/projects/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = ProjectForm(project_fields, request.POST)

        if form.is_valid():

            try:
                project.value.update(form.cleaned_data)
                project.save()

                messages.info(request, 'Project successfully edited.')
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={ 'project_uuid': project.uuid }))
            except Exception as e:
                exception_msg = 'Unable to create new project. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={ 'project_uuid': project.uuid }))


@login_required
@require_http_methods(['GET'])
def delete(request, project_uuid):
    """Delete a project"""
    api_client = request.user.agave_oauth.api_client

    try:
        project = Project(api_client=api_client, uuid=project_uuid)
        project.delete()

        messages.success(request, 'Successfully deleted project.')
        return HttpResponseRedirect('/projects/')
    except Exception as e:
        exception_msg = 'Unable to delete project. %s' % e
        logger.exception(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/projects/')
