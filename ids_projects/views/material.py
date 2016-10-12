from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import logging
from ..forms.material import MaterialTypeForm, MaterialFieldsForm, AddRelationshipForm
from ..models import Project, Specimen, Process, Material
from ids.utils import (get_portal_api_client,
                       get_material_type_keys,
                       get_material_choices,
                       get_material_fields)
from requests import HTTPError

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET'])
def view(request, material_uuid):
    """ """
    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    try:
        material = Material(api_client=api_client, uuid=material_uuid)
        project = material.project
        processes = material.processes
    except Exception as e:
        exception_msg = 'Unable to load material entity. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        material_types = get_material_type_keys(project)
        material_fields = get_material_fields(project, material.value['material_type'])
        material.set_fields(material_fields)
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)

    context = {'material': material,
               'project': project,
               'processes': processes,
               'material_types': material_types}

    return render(request, 'ids_projects/material/detail.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    """Create a new material entity"""

    # get parent uuid (project or specimen), and process type, if inlcuded in
    # the query string

    project_uuid = request.GET.get('project_uuid', None)
    material_type = request.GET.get('material_type', None)

    # check to make sure we have at least one parent uuid (project or specimen)

    if not project_uuid:
        messages.warning(request, 'Missing project, cannot find material entity.')
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    # get the api_client to pass to the model for communication with agave

    api_client = request.user.agave_oauth.api_client

    # instantiate either a project and a specimen, or just a project (specimen
    # objects always have a parent project)

    try:
        project = Project(api_client=api_client, uuid=project_uuid)
    except Exception as e:
        exception_msg = 'Unable to load project, cannot create material entity. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    if project is None:
        exception_msg = 'Missing project, cannot create material entity.'
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    context = {'project': project}

    try:
        material_type_choices = get_material_choices(project)
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

        if material_type is None:
            context['form_material_type'] = MaterialTypeForm(material_type_choices)
            context['form_material_fields'] = None
        else:
            material_type = request.GET.get('material_type')
            process_fields = get_material_fields(project, material_type)

            form_material_type = MaterialTypeForm(material_type_choices, initial={'material_type': material_type})
            form_material_type.fields['material_type'].widget.attrs['disabled'] = True
            form_material_type.fields['material_type'].widget.attrs['readonly'] = True

            form_material_fields = MaterialFieldsForm(process_fields)
            context['form_material_type'] = form_material_type
            context['form_material_fields'] = form_material_fields
            context['material_type'] = material_type

        if request.is_ajax():
            return render(request, 'ids_projects/material/get_fields_ajax.html', context)
        else:
            return render(request, 'ids_projects/material/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        material_type = request.POST.get('material_type')
        material_fields = get_material_fields(project, material_type)

        form_material_type = MaterialTypeForm(material_type_choices, request.POST)
        form_material_type.fields['material_type'].widget.attrs['disabled'] = True
        form_material_type.fields['material_type'].widget.attrs['readonly'] = True

        #################################################
        # POST includes 'form_process_type' fields only #
        #################################################
        if 'material_fields' not in request.POST:
            form_material_fields = MaterialFieldsForm(material_fields)
            context['form_material_type'] = form_material_type
            context['form_material_fields'] = form_material_fields
            context['material_type'] = material_type

        ################################################################
        # POST includes form_process_type & form_process_fields fields #
        ################################################################
        else:
            form_material_fields = MaterialFieldsForm(material_fields, request.POST)

            if form_material_type.is_valid() and form_material_fields.is_valid():

                logger.debug('Material Entity form is valid')

                data = {'material_type': material_type}
                data.update(form_material_type.cleaned_data.copy())
                data.update(form_material_fields.cleaned_data.copy())

                meta = {'value': data}

                try:
                    material = Process(api_client=api_client, meta=meta)
                    material.save()

                    # create two-way relationship to project
                    project.add_material(material)
                    project.save()
                    material.add_project(project)
                    material.save()

                    success_msg = 'Successfully created material entity.'
                    logger.info(success_msg)
                    messages.success(request, success_msg)
                    return HttpResponseRedirect(
                                reverse('ids_projects:material-view',
                                        kwargs={'material_uuid': material.uuid}))
                except HTTPError as e:
                    exception_msg = 'Unable to create new material entity. %s' % e
                    logger.error(exception_msg)
                    messages.error(request, exception_msg)
                    return HttpResponseRedirect(
                                reverse('ids_projects:project-view',
                                        kwargs={'project_uuid': project.uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def add_relationship(request, material_uuid):
    """Edit existing process metadata"""

    api_client = request.user.agave_oauth.api_client

    try:
        material = Material(api_client=api_client, uuid=material_uuid)
        project = material.project
        process_choices = [(x.uuid, x.title) for x in project.processes]
        if material.processes:
            initial = [process.uuid for process in material.processes]
        else:
            initial = None
    except HTTPError as e:
        exception_msg = 'Unable to edit new material entity. %s' % e
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
                   'material': material,
                   'project': material.project}

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
                    process.add_material(material)
                    process.save()

                    material.add_process(process)
                    material.save()

                messages.info(request, 'Successfully added relationship.')
                return HttpResponseRedirect(
                    reverse('ids_projects:material-view',
                            kwargs={'material_uuid': material.uuid}))
            except Exception as e:
                exception_msg = 'Unable to add relationship. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                    reverse('ids_projects:material-view',
                            kwargs={'material_uuid': material.uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def edit(request, material_uuid):
    """Edit existing material entity metadata"""

    api_client = request.user.agave_oauth.api_client

    try:
        material = Material(api_client=api_client, uuid=material_uuid)
    except Exception as e:
        exception_msg = 'Unable to load material entity. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    material_fields = get_material_fields(material.project, material.material_type)

    #######
    # GET #
    #######
    if request.method == 'GET':
        context = {'form_material_edit': MaterialFieldsForm(fields=material_fields, initial=material.value),
                   'project': material.project,
                   'material': material,
                   'processes': material.processes}

        return render(request, 'ids_projects/materiales/edit.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':
        form = MaterialFieldsForm(material_fields, request.POST)

        if form.is_valid():

            try:
                material.value.update(form.cleaned_data)
                material.save()

                messages.info(request, 'Material entity successfully edited.')
                return HttpResponseRedirect(
                            reverse('ids_projects:material-view',
                                    kwargs={'material_uuid': material.uuid}))
            except Exception as e:
                exception_msg = 'Unable to edit material entity. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:material-view',
                                    kwargs={'material_uuid': material.uuid}))


@login_required
@require_http_methods(['GET'])
def delete(request, material_uuid):
    """Delete a material"""
    next_url = request.GET.get('next_url', None)
    api_client = request.user.agave_oauth.api_client

    try:
        material = Material(api_client=api_client, uuid=material_uuid)

        if next_url is None:
            containers = material.containers
            container = next(iter(containers), None)
            if container:
                name = container.name[6:]
                next_url = reverse('ids_projects:%s-view' % name,
                                   kwargs={'%s_uuid' % name: container.uuid})

        material.delete()

        if next_url is not None:
            return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    except Exception as e:
        exception_msg = 'Unable to load data. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))
