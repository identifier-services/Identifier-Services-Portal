from agavepy.agave import Agave, AgaveException
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import (HttpResponse,
                         HttpResponseRedirect,
                         HttpResponseBadRequest,
                         HttpResponseForbidden,
                         HttpResponseNotFound,
                         HttpResponseServerError)
from django.shortcuts import render
import json, logging
from ..forms.specimens import SpecimenForm
from ..models import Project, Specimen
from ids.utils import get_portal_api_client
from helper import client, collapse_meta
from requests import HTTPError

logger = logging.getLogger(__name__)

@login_required
def list(request):
    """List all specimens related to a project"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        project_uuid = request.GET.get('project_uuid', None)

        if not project_uuid:
            messages.warning(request, 'Missing project UUID, cannot find specimens.')
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

        if request.user.is_anonymous():
            api_client = get_portal_api_client()
        else:
            api_client = request.user.agave_oauth.api_client

        try:
            project = Project(api_client=api_client, uuid=project_uuid)
        except Exception as e:
            exception_msg = 'Unable to load project. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect('/projects/private/')

        context = {'project': project, 'specimens': project.specimens}
        return render(request, 'ids_projects/specimens/index.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def view(request, specimen_uuid):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        if request.user.is_anonymous():
            api_client = get_portal_api_client()
        else:
            api_client = request.user.agave_oauth.api_client

        try:
            specimen = Specimen(api_client=api_client, uuid=specimen_uuid)
        except Exception as e:
            exception_msg = 'Unable to load specimen. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect('/projects/private')

        context = { 'project': specimen.project,
                    'specimen': specimen,
                    'processes': specimen.processes }

        return render(request, 'ids_projects/specimens/detail.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def create(request):
    """Create a new specimen related to a project"""
    project_uuid = request.GET.get('project_uuid', False)

    if not project_uuid:
        messages.warning(request, 'Missing project UUID, cannot create specimen.')
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    api_client = request.user.agave_oauth.api_client

    #######
    # GET #
    #######
    if request.method == 'GET':

        try:
            project = Project(api_client=api_client, uuid=project_uuid)
        except Exception as e:
            exception_msg = 'Unable to load project. %s' % e
            logger.exception(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect('/projects/')

        context = {'form_specimen_create': SpecimenForm(),
                   'project': project,
                   'specimen': None}

        return render(request, 'ids_projects/specimens/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = SpecimenForm(request.POST)

        if form.is_valid():

            meta = { 'associationIds':[project_uuid],
                     'value':form.cleaned_data }

            try:
                specimen = Specimen(api_client=api_client, meta=meta)
                result = specimen.save()
            except Exception as e:
                exception_msg = 'Unable to create new specimen. %s' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={'project_uuid': project_uuid}))

            if 'uuid' in result:
                success_msg = 'Successfully created specimen.'
                logger.info(success_msg)
                messages.success(request, success_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:specimen-view',
                                    kwargs={'specimen_uuid': specimen.uuid}))

        warning_msg = 'Invalid API response. %s' % result
        logger.warning(warning_msg)
        messages.warning(request, warning_msg)
        return HttpResponseRedirect(
                        reverse('ids_projects:project-view',
                            kwargs={'project_uuid': project_uuid}))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def edit(request, specimen_uuid):
    """Edit a specimen, given the uuid"""

    api_client = request.user.agave_oauth.api_client

    try:
        specimen = Specimen(api_client=api_client, uuid=specimen_uuid)
    except Exception as e:
        exception_msg = 'Unable to edit specimen. %s' % e
        logger.exception(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/projects/private/')

    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form_specimen_edit': SpecimenForm(initial=specimen.value),
                   'specimen': specimen,
                   'project': specimen.project}

        return render(request, 'ids_projects/specimens/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = SpecimenForm(request.POST)

        if form.is_valid():

            try:
                specimen.value.update(form.cleaned_data)
                result = specimen.save()
            except Exception as e:
                exception_msg = 'Unable to edit specimen. %s' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:specimen-view',
                                    kwargs={'specimen_uuid': specimen.uuid}))

            if 'uuid' in result:
                messages.info(request, 'Specimen successfully edited.')
                return HttpResponseRedirect(
                            reverse('ids_projects:specimen-view',
                                    kwargs={'specimen_uuid': specimen.uuid}))

            warning_msg = 'Invalid API response. %s' % result
            logger.warning(warning_msg)
            messages.warning(request, warning_msg)
            return HttpResponseRedirect(
                        reverse('ids_projects:specimen-view',
                                kwargs={ 'specimen_uuid': specimen.uuid }))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def delete(request, specimen_uuid):
    """Delete a specimen"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        api_client = request.user.agave_oauth.api_client

        try:
            specimen = Specimen(api_client=api_client, uuid=specimen_uuid)
            project = specimen.project
            specimen.delete()
        except Exception as e:
            exception_msg = 'Unable to delete specimen. %s' % e
            logger.exception(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect('/project/{}/'.format(project.uuid))

        messages.success(request, 'Successfully deleted specimen.')
        return HttpResponseRedirect('/project/{}/'.format(project.uuid))

    #########
    # OTHER #
    #########
    else:
        return HttpResponseBadRequest("Method not allowed")
