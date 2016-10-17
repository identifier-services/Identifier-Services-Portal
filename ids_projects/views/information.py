from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import logging
from ..forms.information import InformationTypeForm, InformationFieldsForm, AddRelationshipForm
from ..models import Project, Specimen, Process, Information
from ids.utils import (get_portal_api_client,
                       get_information_type_keys,
                       get_information_choices,
                       get_information_fields)
from requests import HTTPError

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET'])
def view(request, information_uuid):
    """ """
    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    try:
        information = Information(api_client=api_client, uuid=information_uuid)
        project = information.project
        processes = information.processes
    except Exception as e:
        exception_msg = 'Unable to load information entity. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        information_types = get_information_type_keys(project)
        information_fields = get_information_fields(project, information.value['information_type'])
        information.set_fields(information_fields)
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)

    context = {'information': information,
               'project': project,
               'processes': processes,
               'information_types': information_types}

    return render(request, 'ids_projects/information/detail.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    """Create a new information entity"""

    # get parent uuid (project or specimen), and process type, if inlcuded in
    # the query string

    project_uuid = request.GET.get('project_uuid', None)
    information_type = request.GET.get('information_type', None)

    # check to make sure we have at least one parent uuid (project or specimen)

    if not project_uuid:
        messages.warning(request, 'Missing project, cannot find information entity.')
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    # get the api_client to pass to the model for communication with agave

    api_client = request.user.agave_oauth.api_client

    # instantiate either a project and a specimen, or just a project (specimen
    # objects always have a parent project)

    try:
        project = Project(api_client=api_client, uuid=project_uuid)
    except Exception as e:
        exception_msg = 'Unable to load project, cannot create information entity. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    if project is None:
        exception_msg = 'Missing project, cannot create information entity.'
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    context = {'project': project}

    try:
        information_type_choices = get_information_choices(project)
    except Exception as e:
        exception_msg = 'Missing project type information, cannot create process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:project-view',
                            kwargs={'project__uuid': project.uuid}))

    #######
    # GET #
    #######
    if request.method == 'GET':

        if information_type is None:
            context['form_information_type'] = InformationTypeForm(information_type_choices)
            context['form_information_fields'] = None
        else:
            information_type = request.GET.get('information_type')
            process_fields = get_information_fields(project, information_type)

            form_information_type = InformationTypeForm(information_type_choices, initial={'information_type': information_type})
            form_information_type.fields['information_type'].widget.attrs['disabled'] = True
            form_information_type.fields['information_type'].widget.attrs['readonly'] = True

            form_information_fields = InformationFieldsForm(process_fields)
            context['form_information_type'] = form_information_type
            context['form_information_fields'] = form_information_fields
            context['information_type'] = information_type

        if request.is_ajax():
            return render(request, 'ids_projects/information/get_fields_ajax.html', context)
        else:
            return render(request, 'ids_projects/information/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        information_type = request.POST.get('information_type')
        information_fields = get_information_fields(project, information_type)

        form_information_type = InformationTypeForm(information_type_choices, request.POST)
        form_information_type.fields['information_type'].widget.attrs['disabled'] = True
        form_information_type.fields['information_type'].widget.attrs['readonly'] = True

        #################################################
        # POST includes 'form_process_type' fields only #
        #################################################
        if 'information_fields' not in request.POST:
            form_information_fields = InformationFieldsForm(information_fields)
            context['form_information_type'] = form_information_type
            context['form_information_fields'] = form_information_fields
            context['information_type'] = information_type

        ################################################################
        # POST includes form_process_type & form_process_fields fields #
        ################################################################
        else:
            form_information_fields = InformationFieldsForm(information_fields, request.POST)

            if form_information_type.is_valid() and form_information_fields.is_valid():

                logger.debug('Information Entity form is valid')

                data = {'information_type': information_type}
                data.update(form_information_type.cleaned_data.copy())
                data.update(form_information_fields.cleaned_data.copy())

                meta = {'value': data}

                try:
                    information = Process(api_client=api_client, meta=meta)
                    information.save()

                    # create two-way relationship to project
                    project.add_information(information)
                    project.save()
                    information.add_project(project)
                    information.save()

                    success_msg = 'Successfully created information entity.'
                    logger.info(success_msg)
                    messages.success(request, success_msg)
                    return HttpResponseRedirect(
                                reverse('ids_projects:information-view',
                                        kwargs={'information_uuid': information.uuid}))
                except HTTPError as e:
                    exception_msg = 'Unable to create new information entity. %s' % e
                    logger.error(exception_msg)
                    messages.error(request, exception_msg)
                    return HttpResponseRedirect(
                                reverse('ids_projects:project-view',
                                        kwargs={'project_uuid': project.uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def add_relationship(request, information_uuid):
    """Edit existing process metadata"""

    api_client = request.user.agave_oauth.api_client

    try:
        information = Information(api_client=api_client, uuid=information_uuid)
        project = information.project
        process_choices = [(x.uuid, x.title) for x in project.processes]
        if information.processes:
            initial = [process.uuid for process in information.processes]
        else:
            initial = None
    except HTTPError as e:
        exception_msg = 'Unable to edit new information entity. %s' % e
        logger.error(exception_msg)
        messages.error(request, exception_msg)
        return HttpResponseRedirect(
            reverse('ids_projects:project-view',
                    kwargs={'project_uuid': project.uuid}))

    #######
    # GET #
    #######
    if request.method == 'GET':
        context = {'form_add_relationship': AddRelationshipForm(choices=process_choices, initial=initial),
                   'information': information,
                   'project': information.project}

        return render(request, 'ids_projects/mateial/add_relationship.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':
        form = AddRelationshipForm(process_choices, request.POST)

        if form.is_valid():
            try:
                data = form.cleaned_data
                process_choices = data['process_choices']

                for process in process_choices:
                    process.add_information(information)
                    process.save()

                    information.add_process(process)
                    information.save()

                messages.info(request, 'Successfully added relationship.')
                return HttpResponseRedirect(
                    reverse('ids_projects:information-view',
                            kwargs={'information_uuid': information.uuid}))
            except Exception as e:
                exception_msg = 'Unable to add relationship. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                    reverse('ids_projects:information-view',
                            kwargs={'information_uuid': information.uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def edit(request, information_uuid):
    """Edit existing information entity metadata"""

    api_client = request.user.agave_oauth.api_client

    try:
        information = Information(api_client=api_client, uuid=information_uuid)
    except Exception as e:
        exception_msg = 'Unable to load information entity. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    information_fields = get_information_fields(information.project, information.information_type)

    #######
    # GET #
    #######
    if request.method == 'GET':
        context = {'form_information_edit': InformationFieldsForm(fields=information_fields, initial=information.value),
                   'project': information.project,
                   'information': information,
                   'processes': information.processes}

        return render(request, 'ids_projects/informationes/edit.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':
        form = InformationFieldsForm(information_fields, request.POST)

        if form.is_valid():

            try:
                information.value.update(form.cleaned_data)
                information.save()

                messages.info(request, 'Information entity successfully edited.')
                return HttpResponseRedirect(
                            reverse('ids_projects:information-view',
                                    kwargs={'information_uuid': information.uuid}))
            except Exception as e:
                exception_msg = 'Unable to edit information entity. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:information-view',
                                    kwargs={'information_uuid': information.uuid}))


@login_required
@require_http_methods(['GET'])
def delete(request, information_uuid):
    """Delete a information"""
    next_url = request.GET.get('next_url', None)
    api_client = request.user.agave_oauth.api_client

    try:
        information = Information(api_client=api_client, uuid=information_uuid)

        if next_url is None:
            containers = information.containers
            container = next(iter(containers), None)
            if container:
                name = container.name[6:]
                next_url = reverse('ids_projects:%s-view' % name,
                                   kwargs={'%s_uuid' % name: container.uuid})

        information.delete()

        if next_url is not None:
            return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    except Exception as e:
        exception_msg = 'Unable to load data. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))
