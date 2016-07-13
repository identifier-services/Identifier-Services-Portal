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
from ..forms.datasets import DatasetForm
from ..models import Project, Data, Dataset
from ids.utils import get_portal_api_client, get_dataset_fields
from requests import HTTPError

logger = logging.getLogger(__name__)


def list_public(request):
    """List all public datasets in a project"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        api_client = get_portal_api_client()

        try:
            public_datasets = Dataset.list(api_client=api_client)
        except Exception as e:
            exception_msg = 'Unable to load datasets. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

        context = { 'public_datasets': public_datasets }

        return render(request, 'ids_projects/datasets/index.html', context)

    #########
    # OTHER #
    #########
    else:
        return HttpResponseBadRequest("Method not allowed")

@login_required
def list_private(request):
    """List all private datasets in a project"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        api_client = request.user.agave_oauth.api_client
        project_uuid = request.GET.get('project_uuid', None)

        if not project_uuid:
            messages.warning(request, 'Missing project UUID, cannot find datasets.')
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

        try:
            project = Project(api_client=api_client, uuid=project_uuid)
            private_datasets = project.datasets

        except Exception as e:
            exception_msg = 'Unable to load datasets. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

        context = { 'project': project,
                    'private_datasets' : private_datasets
                  }

        return render(request, 'ids_projects/processes/index.html', context)

    #########
    # OTHER #
    #########
    else:
        return HttpResponseBadRequest("Method not allowed")


def view(request, dataset_uuid):
    """View a specific dataset"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        if request.user.is_anonymous():
            api_client = get_portal_api_client()
        else:
            api_client = request.user.agave_oauth.api_client

        try:
            dataset = Dataset(api_client=api_client, uuid=dataset_uuid)
        except Exception as e:
            exception_msg = 'Unable to load process. %s' % e
            logger.error(exception_msg)
            messages.warning(request, exception_msg)
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

        context = { 'project' : dataset.project,
                    'dataset' : dataset,
                    'datas' : dataset.data }

        return render(request, 'ids_projects/processes/detail.html', context)

    #########
    # OTHER #
    #########
    else:
        return HttpResponseBadRequest("Method not allowed")


@login_required
def create(request):
    """Create a new dataset"""

    project_uuid = request.GET.get('project_uuid', None)

    if not project_uuid:
        messages.warning(request, 'Missing project UUID, cannot find processes.')
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    api_client = request.user.agave_oauth.api_client

    try:
        project = Project(api_client=api_client, uuid=project_uuid)
    except Exception as e:
        exception_msg = 'Unable to load project, cannot create dataset. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        dataset_fields = get_dataset_fields(project)
    except Exception as e:
        exception_msg = 'Missing project type information, cannot create dataset. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:project-view',
                            kwargs={'project_uuid': project.uuid}))

    context = { 'project':project }

    #######
    # GET #
    #######
    if request.method == 'GET':

        context['form_dataset_create'] = DatasetForm(fields=dataset_fields)
        return render(request, 'ids_projects/datasets/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form_dataset = DatasetForm(dataset_fields, request.POST)

        if form_dataset.is_valid():
            logger.debug('Dataset form is valid')

            try:
                dataset = Dataset(api_client=api_client)
                dataset.value = form_dataset.cleaned_data
                dataset.associationIds = [project.uuid]
                dataset.save()

                success_msg = 'Successfully created dataset.'
                logger.info(success_msg)
                messages.success(request, success_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:dataset-view',
                                    kwargs={'dataset_uuid': dataset.uuid}))
            except HTTPError as e:
                exception_msg = 'Unable to create new dataset. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={'project_uuid': project.uuid}))

@login_required
def edit(request, dataset_uuid):
    """Edit existing dataset metadata"""

    project_uuid = request.GET.get('project_uuid', None)

    if not project_uuid:
        messages.warning(request, 'Missing project UUID, cannot find processes.')
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    api_client = request.user.agave_oauth.api_client

    try:
        project = Project(api_client=api_client, uuid=project_uuid)
    except Exception as e:
        exception_msg = 'Unable to load project, cannot create dataset. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        dataset_fields = get_dataset_fields(project)
    except Exception as e:
        exception_msg = 'Missing project type information, cannot create dataset. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
                    reverse('ids_projects:project-view',
                            kwargs={'project_uuid': project.uuid}))

    context = { 'project':project }

    #######
    # GET #
    #######
    if request.method == 'GET':

        context['form_dataset_create'] = DatasetForm(fields=dataset_fields)
        return render(request, 'ids_projects/datasets/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form_dataset = DatasetForm(dataset_fields, request.POST)

        if form_dataset.is_valid():
            logger.debug('Dataset form is valid')

            try:
                dataset = Dataset(api_client=api_client)
                dataset.value = form_dataset.cleaned_data
                dataset.associationIds = [project.uuid]
                dataset.save()

                success_msg = 'Successfully created dataset.'
                logger.info(success_msg)
                messages.success(request, success_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:dataset-view',
                                    kwargs={'dataset_uuid': dataset.uuid}))
            except HTTPError as e:
                exception_msg = 'Unable to create new dataset. %s' % e
                logger.error(exception_msg)
                messages.warning(request, exception_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={'project_uuid': project.uuid}))

@login_required
def add_data(self, dataset_uuid):
    pass

@login_required
def remove_data(self, dataset_uuid):
    pass

@login_required
def make_public(self, dataset_uuid):
    pass

@login_required
def make_private(self, dataset_uuid):
    pass

@login_required
def request_doi(self, dataset_uuid):
    pass

@login_required
def delete(request, dataset_uuid):
    """Delete a dataset - if no external identifier is associated with it"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        api_client = request.user.agave_oauth.api_client

        try:
            dataset = Dataset(api_client=api_client, uuid=dataset_uuid)
            specimen = process.specimen
            project = process.project
            process.delete()
        except Exception as e:
            exception_msg = 'Unable to delete process. %s' % e
            logger.exception(exception_msg)
            messages.warning(request, exception_msg)
            if specimen:
                return HttpResponseRedirect('/specimen/{}/'.format(specimen.uuid))
            else:
                return HttpResponseRedirect('/project/{}/'.format(project.uuid))

        messages.success(request, 'Successfully deleted process.')
        if specimen:
            return HttpResponseRedirect('/specimen/{}'.format(specimen.uuid))
        else:
            return HttpResponseRedirect('/project/{}'.format(project.uuid))

    #########
    # OTHER #
    #########
    else:
        return HttpResponseBadRequest("Method not allowed")
