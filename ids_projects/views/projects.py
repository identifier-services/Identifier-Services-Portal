from agavepy.agave import Agave, AgaveException
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import (HttpResponse,
                         HttpResponseRedirect,
                         HttpResponseBadRequest,
                         HttpResponseForbidden,
                         HttpResponseNotFound,
                         HttpResponseServerError)
from django.shortcuts import render
import json, logging
from ..forms.projects import ProjectForm


logger = logging.getLogger(__name__)


def _client(request):
    token = request.session.get(getattr(settings, 'AGAVE_TOKEN_SESSION_ID'))
    access_token = token.get('access_token', None)
    logger.debug("access token: {}".format(access_token))
    url = getattr(settings, 'AGAVE_TENANT_BASEURL')
    return Agave(api_server = url, token = access_token)


def _collaps_meta(x):
    d = x['value']
    d['uuid'] = x['uuid']
    return d


@login_required
def list(request):
    """List all projects"""
    #######
    # GET #
    #######
    if request.method == 'GET':
        a = _client(request)
        query = {'name':'idsvc.project'}
        projects_raw = a.meta.listMetadata(q=json.dumps(query))
        projects = map(_collaps_meta, projects_raw)

        context = {'projects':projects}

        return render(request, 'ids_projects/projects/index.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


def view(request, project_id):
    """Queries project metadata and all associated metadata"""
    # TODO: Performance in this view is pretty bad
    # TODO: need to cut down on number of requests being made to agave tenant
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = _client(request)
        project_raw = a.meta.getMetadata(uuid=project_id)
        project = _collaps_meta(project_raw)
        # project = a.meta.getMetadata(uuid=project_id)
        # project['specimens'] = []
        #
        associationIds = [project_id]
        #
        # query = {'associationIds': { '$in': associationIds }}
        # results = a.meta.listMetadata(q=json.dumps(query))
        #
        # specimens = {}
        # processes = {}
        # files = {}
        #
        # for result in results:
        #     uuid = result['uuid']
        #     name = result['name']
        #     if name == 'idsvc.specimen':
        #         result['processes'] = []
        #         specimens[uuid] = result
        #     elif name == 'idsvc.process':
        #         result['files'] = []
        #         processes[uuid].append(result)
        #     elif name == 'idsvc.data':
        #         files[uuid] = result
        #
        # specimen_ids = specimens.iterkeys()
        # process_ids = processes.iterkeys()
        # file_ids = files.iterkeys()
        #
        # unmatched_processes = []
        # unmatched_files = []
        #
        # for file_id in file_ids:
        #     file_data = files[file_id]
        #     associations = file_data['associationIds']
        #     match = filter(lambda x: x in associationIds, process_ids)
        #     if match:
        #         process_id = match[0]
        #         processes[process_id]['files'].append(file_data)
        #     else:
        #         unmatched_files.append(file_data)
        #
        # for process_id in process_ids:
        #     process = processes[process_id]
        #     associations = process['associationIds']
        #     match = filter(lambda x: x in associationIds, specimen_ids)
        #     if match:
        #         specimen_id = match[0]
        #         specimens[specimen_id]['processes'].append(process)
        #     else:
        #         unmatched_processes.append(process)
        #
        # for specimen_id in specimen_ids:
        #     specimen = specimens[specimen_id]
        #     project['specimens'].append(specimen)

        specimens_query = {'associationIds': { '$in': associationIds }}
        specimens_raw = a.meta.listMetadata(q=json.dumps(specimens_query))
        specimens = map(_collaps_meta, specimens_raw)

        specimen_count = len(specimens)
        process_count = 0
        file_count = 0

        for specimen in specimens:
            specimen_id = specimen['uuid']
            process_query = {'name':'idsvc.process','associationIds':'{}'.format(specimen_id)}
            processes_raw = a.meta.listMetadata(q=json.dumps(process_query))
            processes = map(_collaps_meta, processes_raw)
            for process in processes:
                process_id = process['uuid']
                files_query = {'name':'idsvc.data','associationIds':'{}'.format(process_id)}
                files_raw = a.meta.listMetadata(q=json.dumps(files_query))
                files = map(_collaps_meta, files_raw)
                process['files'] = files
                file_count += 1
            specimen['processes'] = processes
            process_count += 1
        project['specimens'] = specimens

        context = {'project' : project,
                   'specimen_count' : specimen_count,
                   'process_count' : process_count,
                   'file_count' : file_count,}

        #return HttpResponse(json.dumps(context),status = 200, content_type='application/json')
        return render(request, 'ids_projects/projects/detail.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def create(request):
    """Create a new project"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form': ProjectForm()}
        return render(request, 'ids_projects/projects/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = ProjectForm(request.POST)

        if form.is_valid():

            user_full = request.user.get_full_name()

            title = form.cleaned_data['title']
            inv_type = form.cleaned_data['investigation_type']
            desc = form.cleaned_data['description']

            new_project = {
                'name' : 'idsvc.project',
                'associationIds' : [],
                'value' : {
                    'title' : title,
                    'creator' : user_full,
                    'investigation_type' : inv_type,
                    'description' : desc,
                },
            }

            import pdb;

            a = _client(request)

            try:
                response = a.meta.addMetadata(body=new_project)
            except Exception as e:
                logger.debug('Error while attempting to create project metadata: %s' % e)
            else:
                messages.success(request, 'Successfully created project.')
                return HttpResponseRedirect('/project/{}'.format(response['uuid']))

        messages.info(request, 'Did not create new project.')
        return HttpResponseRedirect('/projects/')

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def edit(request, project_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = _client(request)
        try:
            project = a.meta.getMetadata(uuid=project_id)
        except:
            return HttpResponseNotFound("Project not found")
        else:
            context = {'form': ProjectForm(initial=project)}
            return render(request, 'ids_projects/projects/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = ProjectForm(request.POST)

        if form.is_valid():

            user_full = request.user.get_full_name()

            title = form.cleaned_data['title']
            inv_type = form.cleaned_data['investigation_type']
            desc = form.cleaned_data['description']

            new_project = {
                'name' : 'idsvc.project',
                'associationIds' : [],
                'value' : {
                    'title' : title,
                    'creator' : user_full,
                    'investigation_type' : inv_type,
                    'description' : desc,
                },
            }

            a = _client(request)
            try:
                response = a.meta.updateMetadata(uuid=project_id, body=new_project)
            except Exception as e:
                logger.exception('Error while attempting to edit project metadata.')

        # TODO: check to see if anything actually changed
        messages.success(request, 'Successfully edited project.')
        return HttpResponseRedirect('/projects/')

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def delete(request, project_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = _client(request)

        query = {'associationIds':'{}'.format(project_id)}
        results = a.meta.listMetadata(q=json.dumps(query))

        for result in results:
            a.meta.deleteMetadata(uuid=result.uuid)

        try:
            a.meta.deleteMetadata(uuid=project_id)
        except:
            logger.exception('Error deleting project.')
            messages.error(request, 'Project deletion unsuccessful.')
            # return HttpResponseServerError("Error deleting project.")
            return HttpResponseRedirect('/projects/')
        else:
            messages.success(request, 'Successfully deleted project.')
            return HttpResponseRedirect('/projects/')

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")
