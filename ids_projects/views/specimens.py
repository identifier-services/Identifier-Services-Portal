from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from ..forms.specimens import SpecimenForm
from ..models import Project, Specimen
from ids.utils import (get_portal_api_client,
                       get_process_type_keys,
                       get_specimen_fields)
from ..forms.upload_option import UploadOptionForm, UploadFileForm

from ids_projects.tasks import bulk_specimen_registration

import logging
import csv
import traceback

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

        context = {'project': project,
                   'specimen': specimen,
                   'processes': processes,
                   'process_types': process_types}

        return render(request, 'ids_projects/specimens/detail.html', context)
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

@login_required
@require_http_methods(['GET','POST'])
def upload_option(request):
    project_uuid = request.GET.get('project_uuid', False)

    if not project_uuid:
        messages.warning(request, 'Missing project UUID, cannot create specimen.')
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    project = Project(api_client=api_client, uuid=project_uuid)

    # POST
    if request.method == 'POST':
        context = {'project': project}

        if request.POST.get('upload_option', None) == 'Single':
            # Single Specimen
            url = "%s?project_uuid=%s" % (reverse('ids_projects:specimen-create'), project_uuid)
            return HttpResponseRedirect(url)


        elif request.POST.get('upload_option', None) == 'Bulk':

            try:
                specimens_meta = _validate_specimens(request.FILES['file'], project)
                bulk_specimen_registration.apply_async(args=(specimens_meta,
                                                             project_uuid,
                                                             request.user.username), serilizer='json')

                success_msg = 'Your %d specimens have been in the registration queue.' % len(specimens_meta)
                logger.info(success_msg)
                messages.success(request, success_msg)
                return HttpResponseRedirect(
                                reverse('ids_projects:project-view',
                                        kwargs={'project_uuid': project.uuid}))

            except Exception as e:
                traceback.print_exc()
                exception_msg = repr(e)
                logger.error(exception_msg)
                messages.warning(request, exception_msg)

                return HttpResponseRedirect(
                                reverse('ids_projects:project-view',
                                        kwargs={'project_uuid': project.uuid}))

    # GET
    else:
        context = {'project': project}
        context['form_upload_file'] = UploadFileForm()
        context['form_upload_option'] = UploadOptionForm()
        return render(request, 'ids_projects/specimens/upload_option.html', context)

def _validate_specimens(f, project):
    """ process uploaded csv file to register specimens """
    # NEED TO ADD VALIDATION

    header = True

    specimen_fields = get_specimen_fields(project)

    logger.debug("Specimen fields: {}".format(specimen_fields))

    reader = csv.reader(f)
    row_num = 0
    specimens_meta = []

    if header:
        row = next(reader, None)
        for index in range(len(row)):
            if row[index].lower() != specimen_fields[index]['id']:
                raise Exception("Fields does not match!")
            else:
                logger.debug("Field match OK: %s" % row[index])

    # reading metadata
    for row in reader:
        meta = {}
        col_num = 0

        for field in specimen_fields[:-1]:
            meta[field['id']] = row[col_num]
            col_num = col_num + 1

        specimens_meta.append(meta)
        row_num = row_num + 1

    logger.debug("Specimens meta: {}".format(specimens_meta))

    return specimens_meta


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

    try:
        specimen_fields = get_specimen_fields(project)
    except Exception as e:
        exception_msg = 'Missing project type information, cannot create specimen. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:project-view',
                            kwargs={'project_uuid': project.uuid}))

    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form_specimen_create': SpecimenForm(specimen_fields),
                   'project': project,
                   'specimen': None}

        return render(request, 'ids_projects/specimens/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = SpecimenForm(specimen_fields, request.POST)

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
        project = specimen.project
    except Exception as e:
        exception_msg = 'Unable to edit specimen. %s' % e
        logger.exception(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/projects/')

    try:
        specimen_fields = get_specimen_fields(project)
    except Exception as e:
        exception_msg = 'Missing project type information, cannot edit specimen. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:project-view',
                            kwargs={'project_uuid': project.uuid}))

    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form_specimen_edit': SpecimenForm(fields=specimen_fields, initial=specimen.value),
                   'specimen': specimen,
                   'project': specimen.project}

        return render(request, 'ids_projects/specimens/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = SpecimenForm(specimen_fields, request.POST)

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
