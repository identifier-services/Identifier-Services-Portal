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
    url = getattr(settings, 'AGAVE_TENANT_BASEURL')
    return Agave(api_server = url, token = access_token)


def _collaps_meta(x):
    d = x['value']
    d['uuid'] = x['uuid']
    return d


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

        specimens_query = {'name':'idsvc.specimen','associationIds':'{}'.format(project_id)}
        specimens_raw = a.meta.listMetadata(q=json.dumps(specimens_query))
        specimens = map(_collaps_meta, specimens_raw)

        for specimen in specimens:
            specimen_id = specimen['uuid']
            process_query = {'name':'idsvc.process','associationIds':'{}'.format(specimen_id)}
            processes_raw = a.meta.listMetadata(q=json.dumps(specimens_query))
            processes = map(_collaps_meta, processes_raw)
            for process in processes:
                process_id = process['uuid']
                files_query = {'name':'idsvc.data','associationIds':'{}'.format(process_id)}
                files_raw = a.meta.listMetadata(q=json.dumps(files_query))
                files = map(_collaps_meta, files_raw)
                process['files'] = files
            specimen['processes'] = processes
        project['specimens'] = specimens

        context = {'project' : project,}

        print context

        #return HttpResponse(json.dumps(context),status = 200, content_type='application/json')
        return render(request, 'ids_projects/projects/detail.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


def create(request):
    """ """
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

            a = _client(request)
            try:
                response = a.meta.addMetadata(body=new_project)
            except Exception as e:
                logger.debug('Error while attempting to create project metadata: %s' % e)
            else:
                # import pdb; pdb.set_trace()
                messages.success(request, 'Successfully created project.')
                return HttpResponseRedirect('/project/{}'.format(response['uuid']))

        messages.info(request, 'Did not create new project.')
        return HttpResponseRedirect('/projects/')

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


def edit(request, project_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = _client(request)
        query = {'uuid':project_id}
        project_list = a.meta.listMetadata(q=json.dumps(query))

        try:
            project = project_list[0]
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


def delete(request, project_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = _client(request)

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
