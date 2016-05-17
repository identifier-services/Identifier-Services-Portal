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
            return HttpResponseRedirect(reverse('ids_projects:project-list'))

        try:
            project = Project(uuid=project_uuid, user=request.user)
        except Exception as e:
            exception_msg = 'Unable to load project. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect('/projects/')

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

        try:
            specimen = Specimen(uuid = specimen_uuid, user=request.user)
        except Exception as e:
            exception_msg = 'Unable to load specimen. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect('/projects/')

        context = { 'specimen': specimen, 'project': specimen.project }

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
        return HttpResponseRedirect(reverse('ids_projects:project-list'))

    #######
    # GET #
    #######
    if request.method == 'GET':

        try:
            project = Project(uuid=project_uuid, user=request.user)
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

            body = { 'associationIds':[project_uuid],
                     'value':form.cleaned_data }

            try:
                specimen = Specimen(initial_data=body, user=request.user)
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
    """ """
    try:
        specimen = Specimen(uuid=specimen_uuid, user=request.user)
    except Exception as e:
        exception_msg = 'Unable to edit specimen. %s' % e
        logger.exception(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/projects/')

    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form_specimen_edit': SpecimenForm(initial=specimen.body),
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
                # will not overwrite association ids
                body = { 'value': form.cleaned_data }
                specimen.set_initial(body)
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
                    reverse('ids_projects:project-view',
                            kwargs={ 'project_uuid': project.uuid }))

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

        # TODO: Ask user if process and file data should be deleted

        try:
            specimen = Specimen(uuid=specimen_uuid, user=request.user)
        except Exception as e:
            exception_msg = 'Unable to load specimen. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect('/projects/')

        for process in specimen.processes:
            try:
                process.delete()
            except Exception as e:
                exception_msg = 'Unable to delete process. %s' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)

        for data in specimen.data:
            try:
                data.delete()
            except Exception as e:
                exception_msg = 'Unable to delete data. %s' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)

        try:
            specimen.delete()
        except Exception as e:
            exception_msg = 'Unable to delete specimen. %s' % e
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
