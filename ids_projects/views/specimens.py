from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import logging
from ..forms.specimens import SpecimenForm
from ..models import Project, Specimen
from ids.utils import (get_portal_api_client,
                       get_process_type_keys,
                       get_specimen_fields)

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET'])
def list(request):
    """List all specimens related to a project"""
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
        return HttpResponseRedirect('/projects/')

    context = {'project': project, 'specimens': project.specimens}
    return render(request, 'ids_projects/specimens/index.html', context)


@login_required
@require_http_methods(['GET'])
def view(request, specimen_uuid):
    """ """
    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    try:
        specimen = Specimen(api_client=api_client, uuid=specimen_uuid)
        project = specimen.project
        processes = specimen.processes
    except Exception as e:
        exception_msg = 'Unable to load specimen. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/projects')

    try:
        process_types = get_process_type_keys(project)
        specimen_fields = get_specimen_fields(project)
        specimen.set_fields(specimen_fields)
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)

    context = { 'project': project,
                'specimen': specimen,
                'processes': processes,
                'process_types': process_types }

    return render(request, 'ids_projects/specimens/detail.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    """Create a new specimen related to a project"""
    project_uuid = request.GET.get('project_uuid', False)

    if not project_uuid:
        messages.warning(request, 'Missing project UUID, cannot create specimen.')
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    api_client = request.user.agave_oauth.api_client

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

            meta = {'value': form.cleaned_data}

            try:
                specimen = Specimen(api_client=api_client, meta=meta)
                specimen.save()

                # create two-way relationship to project

                # add_part: specimen
                project.add_specimen(specimen)
                project.save()

                # add_container: project
                specimen.add_project(project)
                specimen.save()

                success_msg = 'Successfully created specimen.'
                logger.info(success_msg)
                messages.success(request, success_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:specimen-view',
                                    kwargs={'specimen_uuid': specimen.uuid}))
            except Exception as e:
                exception_msg = 'Unable to create new specimen. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={'project_uuid': project_uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def edit(request, specimen_uuid):
    """Edit a specimen, given the uuid"""

    api_client = request.user.agave_oauth.api_client

    try:
        specimen = Specimen(api_client=api_client, uuid=specimen_uuid)
    except Exception as e:
        exception_msg = 'Unable to edit specimen. %s' % e
        logger.exception(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/projects/')

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
                specimen.save()

                messages.info(request, 'Specimen successfully edited.')
                return HttpResponseRedirect(
                            reverse('ids_projects:specimen-view',
                                    kwargs={'specimen_uuid': specimen.uuid}))
            except Exception as e:
                exception_msg = 'Unable to edit specimen. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:specimen-view',
                                    kwargs={'specimen_uuid': specimen.uuid}))


@login_required
@require_http_methods(['GET'])
def delete(request, specimen_uuid):
    """Delete a specimen"""
    api_client = request.user.agave_oauth.api_client

    try:
        specimen = Specimen(api_client=api_client, uuid=specimen_uuid)
        project = specimen.project
        specimen.delete()

        messages.success(request, 'Successfully deleted specimen.')
        return HttpResponseRedirect('/project/{}/'.format(project.uuid))
    except Exception as e:
        exception_msg = 'Unable to delete specimen. %s' % e
        logger.exception(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/project/{}/'.format(project.uuid))
