from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from ..models import Project, Probe
from ids.utils import (get_portal_api_client,
                       get_probe_fields)

from ..forms.upload_option import UploadOptionForm, UploadFileForm

from ids_projects.tasks import bulk_probe_registration

import logging
import csv
import traceback

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET'])
def view(request, probe_uuid):
    """ """
    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    try:
        probe = Probe(api_client=api_client, uuid=probe_uuid)
        project = probe.project
        processes = probe.processes
    except Exception as e:
        exception_msg = 'Unable to load probe. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/projects')

    try:
        process_types = get_process_type_keys(project)
        probe_fields = get_probe_fields(project)
        probe.set_fields(probe_fields)

        context = {'project': project,
                   'probe': probe,
                   'processes': processes,
                   'process_types': process_types}

        return render(request, 'ids_projects/probes/detail.html', context)
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))


@login_required
@require_http_methods(['GET', 'POST'])
def upload_option(request):
    project_uuid = request.GET.get('project_uuid', False)

    if not project_uuid:

        message.warning(request, 'Missing project UUID, cannot create probe.')
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
            return HttpResponseRedirect(reverse('ids_projects:project-view', kwargs={'project_uuid': project.uuid}))
        else:
            try:
                print request.POST.get('upload_option', None)
                probes_meta = _validate_probes(request.FILES['file'], project)
                bulk_probe_registration.apply_async(args=(probes_meta, project_uuid, request.user.username), serializer='json')

                success_msg = 'Your %d probes have been in the registration queue.' % len(probes_meta)
                logger.info(success_msg)
                messages.success(request, success_msg)
                return HttpResponseRedirect(reverse('ids_projects:project-view', kwargs={'project_uuid': project.uuid}))

            except Exception as e:
                traceback.print_exc()
                exception_msg = repr(e)
                logger.error(exception_msg)
                messages.warning(request, exception_msg)

                return HttpResponseRedirect(reverse('ids_projects:project-view', kwargs={'project_uuid': project_uuid}))

    # GET
    else:
        print "GET method"
        context = {'project': project}
        context['form_upload_file'] = UploadFileForm()
        context['form_upload_option'] = UploadOptionForm()
        return render(request, 'ids_projects/probes/upload_option.html', context)


def _validate_probes(f, project):
    header = True
    row_num = 0
    probes_meta = []

    probe_fields = get_probe_fields(project)
    fields_length = len(probe_fields)

    reader = csv.reader(f)

    if header:
        row = next(reader, None)
        i = 0
        for index in range(fields_length):
            if row[index].lower() != probe_fields[index]['id']:
                raise Exception("Fields does not match!")
            else:
                logger.dedbug("Field match OK: %s" % row[index])

    for row in reader:
        meta = {}
        col_num = 0
        for field in probe_fields:
            meta[field['id']] = row[col_num]
            col_num = col_num + 1

        probes_meta.append(meta)
        row_num = row_num + 1

    # pprint.pprint(probes_meta[0])
    return probes_meta

@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    print "in the probe create view"
    """Create a new probe related to a project"""
    project_uuid = request.GET.get('project_uuid', False)

    if not project_uuid:
        messages.warning(request, 'Missing project UUID, cannot create probe.')
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
        probe_fields = get_probe_fields(project)
    except Exception as e:
        exception_msg = 'Missing project type information, cannot create probe. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:project-view',
                            kwargs={'project_uuid': project.uuid}))

    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form_probe_create': ProbeForm(probe_fields),
                   'project': project,
                   'probe': None}

        return render(request, 'ids_projects/probes/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = ProbeForm(probe_fields, request.POST)
        print request.POST
        print probe_fields

        if form.is_valid():

            meta = {'value': form.cleaned_data}
            print meta

            try:
                probe = Probe(api_client=api_client, meta=meta)
                probe.save()

                # create two-way relationship to project

                # add_part: probe
                project.add_probe(probe)
                project.save()

                # add_container: project
                probe.add_project(project)
                probe.save()

                success_msg = 'Successfully created probe.'
                logger.info(success_msg)
                messages.success(request, success_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:probe-view',
                                    kwargs={'probe_uuid': probe.uuid}))
            except Exception as e:
                exception_msg = 'Unable to create new probe. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={'project_uuid': project_uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def edit(request, probe_uuid):
    """Edit a probe, given the uuid"""

    api_client = request.user.agave_oauth.api_client

    try:
        probe = Probe(api_client=api_client, uuid=probe_uuid)
        project = probe.project
    except Exception as e:
        exception_msg = 'Unable to edit probe. %s' % e
        logger.exception(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/projects/')

    try:
        probe_fields = get_probe_fields(project)
    except Exception as e:
        exception_msg = 'Missing project type information, cannot edit probe. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:project-view',
                            kwargs={'project_uuid': project.uuid}))

    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form_probe_edit': ProbeForm(fields=probe_fields, initial=probe.value),
                   'probe': probe,
                   'project': probe.project}

        return render(request, 'ids_projects/probes/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = ProbeForm(probe_fields, request.POST)

        if form.is_valid():

            try:
                probe.value.update(form.cleaned_data)
                probe.save()

                messages.info(request, 'Probe successfully edited.')
                return HttpResponseRedirect(
                            reverse('ids_projects:probe-view',
                                    kwargs={'probe_uuid': probe.uuid}))
            except Exception as e:
                exception_msg = 'Unable to edit probe. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:probe-view',
                                    kwargs={'probe_uuid': probe.uuid}))


@login_required
@require_http_methods(['GET'])
def delete(request, probe_uuid):
    """Delete a probe"""
    api_client = request.user.agave_oauth.api_client

    try:
        probe = Probe(api_client=api_client, uuid=probe_uuid)
        project = probe.project
        probe.delete()

        messages.success(request, 'Successfully deleted probe.')
        return HttpResponseRedirect('/project/{}/'.format(project.uuid))
    except Exception as e:
        exception_msg = 'Unable to delete probe. %s' % e
        logger.exception(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/project/{}/'.format(project.uuid))
