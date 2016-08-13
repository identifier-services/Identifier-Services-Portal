from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import logging
from ..forms.datasets import DatasetForm, DataSelectForm
from ..models import Project, Specimen, Process, Dataset, Data
from ids.utils import (get_portal_api_client,
                       get_process_type_keys,
                       get_dataset_fields)
from requests import HTTPError
import urllib

logger = logging.getLogger(__name__)


@require_http_methods(['GET'])
def list_public(request):
    """List all public datasets in a project"""
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


@login_required
@require_http_methods(['GET'])
def list_private(request):
    """List all private datasets in a project"""
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
                'private_datasets': private_datasets
              }

    return render(request, 'ids_projects/processes/index.html', context)


@require_http_methods(['GET'])
def view(request, dataset_uuid):
    """View a specific dataset"""
    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    try:
        dataset = Dataset(api_client=api_client, uuid=dataset_uuid)
        project = dataset.project
        data = dataset.data
    except Exception as e:
        exception_msg = 'Unable to load process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        process_types = get_process_type_keys(project)
        dataset_fields = get_dataset_fields(project)
        dataset.set_fields(dataset_fields)
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)

    context = { 'project': project,
                'dataset': dataset,
                'datas': data,
                'process_types': process_types }

    return render(request, 'ids_projects/datasets/detail.html', context)


@require_http_methods(['GET', 'POST'])
@login_required
def select_data(request, dataset_uuid):
    """List data to add to dataset."""
    api_client = request.user.agave_oauth.api_client

    try:
        dataset = Dataset(api_client=api_client, uuid=dataset_uuid)
        project = dataset.project
    except Exception as e:
        exception_msg = 'Unable to load process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:
        process_types = get_process_type_keys(project)
        dataset_fields = get_dataset_fields(project)
        dataset.set_fields(dataset_fields)
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)

    #######
    # GET #
    #######
    if request.method == 'GET':
        data = [x.uuid for x in dataset.data]

        context = {'project': project,
                   'dataset': dataset,
                   'datas': data,
                   'process_types': process_types}

        return render(request, 'ids_projects/datasets/select_data.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        # TODO: this is probably not the best way to do this
        body = urllib.unquote(request.body)

        response_tuples= []
        selected_data = []

        if body:
            response_tuples = map(lambda x: (x.split('=')[0], x.split('=')[1]), body.split('&'))
            selected_data = []
            for key, value in response_tuples:
                selected_data.append(value)

        data_choices = [x.uuid for x in project.data]
        unchecked = list(set(data_choices) - set(selected_data))

        try:
            # TODO: this is very inefficient
            for data_uuid in unchecked:
                data = Data(api_client=api_client, uuid=data_uuid)
                if data in dataset.data:
                    data.remove_container(dataset)
                    data.save()
                    dataset.remove_part(data)

                    print 'removing: %s' % data.name

            dataset.save()

            for data_uuid in selected_data:
                data = Data(api_client=api_client, uuid=data_uuid)
                if data not in dataset.data:
                    data.add_container(dataset)
                    data.save()
                    dataset.add_part(data)

                    print 'adding: %s' % data.name

            dataset.save()

            success_msg = 'Successfully added data to dataset.'
            logger.info(success_msg)
            messages.success(request, success_msg)

            redirect_url = reverse('ids_projects:dataset-view', kwargs={'dataset_uuid': dataset.uuid})

            print 'redirect url: {}'.format(redirect_url)

            return HttpResponseRedirect(redirect_url)

        except HTTPError as e:
            exception_msg = 'Unable to select data. %s' % e
            logger.error(exception_msg)
            messages.error(request, exception_msg)
            return HttpResponseRedirect(
                reverse('ids_projects:dataset-view',
                        kwargs={'dataset_uuid': dataset.uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
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

    context = {'project': project}

    # data_choices = [(x.uuid, x.title) for x in project.data]

    #######
    # GET #
    #######
    if request.method == 'GET':

        # context['form_dataset_create'] = DatasetForm(fields=dataset_fields, choices=data_choices)
        context['form_dataset_create'] = DatasetForm(fields=dataset_fields)
        return render(request, 'ids_projects/datasets/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        #form_dataset = DatasetForm(fields=dataset_fields, choices=data_choices, initial=request.POST)
        form_dataset = DatasetForm(dataset_fields, request.POST)

        if form_dataset.is_valid():
            logger.debug('Dataset form is valid')

            try:

                dataset = Dataset(api_client=api_client, value=form_dataset.cleaned_data)
                dataset.save()

                # create two-way relationship to project
                project.add_part(dataset)
                project.save()

                dataset.add_container(project)
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

        else:
            exception_msg = "Dataset form is not valid!"
            logger.error(exception_msg)
            messages.error(request, exception_msg)
            return HttpResponseRedirect(
                reverse('ids_projects:project-view',
                        kwargs={'project_uuid': project.uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def edit(request, dataset_uuid):
    """Edit existing dataset metadata"""
    api_client = request.user.agave_oauth.api_client

    try:
        dataset = Dataset(api_client=api_client, uuid=dataset_uuid)
        project = dataset.project
    except Exception as e:
        exception_msg = 'Unable to edit dataset. %s' % e
        logger.exception(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect('/projects/')

    try:
        dataset_fields = get_dataset_fields(project)
    except Exception as e:
        exception_msg = 'Missing project type information, cannot edit dataset. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(
            reverse('ids_projects:project-view',
                    kwargs={'project_uuid': project.uuid}))

    # data_choices = [(x.uuid, x.title) for x in project.data]

    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form_dataset_edit': DatasetForm(dataset_fields, dataset.value),
                   'dataset': dataset,
                   'project': project}

        return render(request, 'ids_projects/datasets/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = DatasetForm(dataset_fields, request.POST)

        if form.is_valid():

            try:
                dataset.value.update(form.cleaned_data)
                dataset.save()

                messages.info(request, 'Dataset successfully edited.')
                return HttpResponseRedirect(
                    reverse('ids_projects:dataset-view',
                            kwargs={'dataset_uuid': dataset.uuid}))
            except Exception as e:
                exception_msg = 'Unable to edit specimen. %s' % e
                logger.error(exception_msg)
                messages.error(request, exception_msg)
                return HttpResponseRedirect(
                    reverse('ids_projects:dataset-view',
                            kwargs={'dataset_uuid': dataset.uuid}))

        else:
            exception_msg = "Dataset form is not valid!"
            logger.error(exception_msg)
            messages.error(request, exception_msg)
            return HttpResponseRedirect(
                reverse('ids_projects:dataset-view',
                        kwargs={'dataset_uuid': dataset.uuid}))


@login_required
@require_http_methods(['GET', 'POST'])
def add_data(request, dataset_uuid):
    api_client = request.user.agave_oauth.api_client

    import pdb;
    pdb.set_trace()

    try:
        dataset = Dataset(api_client=api_client, uuid=dataset_uuid)
        project = dataset.project
    except Exception as e:
        exception_msg = 'Unable to load process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))


@login_required
@require_http_methods(['GET', 'POST'])
def remove_data(request, dataset_uuid):
    # TODO: this is not done
    logger.warning('Remove Data not implemented, see Dataset view.')
    return HttpResponseNotFound()


@login_required
@require_http_methods(['GET'])
def make_public(request, dataset_uuid):
    # TODO: this is not done
    logger.warning('Make Public not implemented, see Dataset view.')
    return HttpResponseNotFound()


@login_required
@require_http_methods(['GET'])
def make_private(request, dataset_uuid):
    # TODO: this is not done
    logger.warning('Make Private not implemented, see Dataset view.')
    return HttpResponseNotFound()


# @login_required
@require_http_methods(['GET', 'POST'])
def request_doi(request, dataset_uuid):
    # # TODO: this is not done
    # logger.warning('Request DOI not implemented, see Dataset view.')
    # return HttpResponseNotFound()

    if request.method == 'GET':
        context = {}

        return render(request, 'ids_projects/datasets/request_doi.html', context)

    if request.method == 'POST':

        body = urllib.unquote(request.body)
        response_tuples = map(lambda x: (x.split('=')[0], x.split('=')[1]), body.split('&'))
        response = {}
        for key, value in response_tuples:
            response[key] = value

        # import pdb; pdb.set_trace()

        print response

        context = {}

        success_msg = 'Something was successful.'
        logger.info(success_msg)
        messages.success(request, success_msg)

        return HttpResponseRedirect('/')


# @login_required
@require_http_methods(['GET', 'POST'])
def request_doi2(request, dataset_uuid):
    # # TODO: this is not done
    # logger.warning('Request DOI not implemented, see Dataset view.')
    # return HttpResponseNotFound()

    if request.method == 'GET':
        context = {}

        success_msg = 'Something was successful.'
        logger.info(success_msg)
        messages.success(request, success_msg)

        return HttpResponseRedirect('/')

    if request.method == 'POST':
        context = {}

        success_msg = 'Something was successful.'
        logger.info(success_msg)
        messages.success(request, success_msg)

        return HttpResponseRedirect('/')


@login_required
@require_http_methods(['GET'])
def delete(request, dataset_uuid):
    """Delete a dataset - if no external identifier is associated with it"""
    next_url = request.GET.get('next_url', None)
    api_client = request.user.agave_oauth.api_client

    try:
        dataset = Dataset(api_client=api_client, uuid=dataset_uuid)

        if next_url is None:
            containers = dataset.containers
            container = next(iter(containers), None)
            if container:
                name = container.name[6:]
                next_url = reverse('ids_projects:%s-view' % name,
                                   kwargs={'%s_uuid' % name: container.uuid})

        dataset.delete()

        if next_url is not None:
            return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    except Exception as e:
        exception_msg = 'Unable to load data. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))
