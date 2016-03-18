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
from helper import client, collapse_meta


logger = logging.getLogger(__name__)


@login_required
def list(request):
    """List all projects"""
    #######
    # GET #
    #######
    if request.method == 'GET':
        a = client(request)
        query = {'name':'idsvc.project'}
        projects_raw = a.meta.listMetadata(q=json.dumps(query))
        projects = map(collapse_meta, projects_raw)

        context = {'projects':projects}

        return render(request, 'ids_projects/projects/index.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


def view(request, project_uuid):
    """Queries project metadata and all associated metadata"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        # get the project meta
        a = client(request)
        project_raw = a.meta.getMetadata(uuid=project_uuid)
        project = collapse_meta(project_raw)
        # list for the project's specimens
        project['specimens'] = []

        # get everything related to the project (everything with the
        # project_uuid in associationIds)
        query = {'associationIds': project_uuid }
        results_raw = a.meta.listMetadata(q=json.dumps(query))
        results = map(collapse_meta, results_raw)

        # create dicts to hold objects, key will be object uuid
        specimens = {}
        processes = {}
        files = {}

        # group by type
        for result in results:
            uuid = result['uuid']
            name = result['name']
            if name == 'idsvc.specimen':
                # let's call the result a specimen
                specimen = result
                # create a list for processes
                specimen['processes'] = []
                # add to dictionary
                specimens[uuid] = specimen
            elif name == 'idsvc.process':
                # let's call the result a process
                process = result
                # create a list for file metadata
                process['files'] = []
                # add to dictionary
                processes[uuid] = process
            elif name == 'idsvc.data':
                # let's call the result file_data
                file_data = result
                # add to dictionary
                files[uuid] = file_data


        # get list of uuids for each object type
        specimen_uuids = specimens.keys()
        process_uuids = processes.keys()
        file_ids = files.keys()

        # place to put object created 'out of order'
        unmatched_processes = []
        unmatched_files = []

        # match files to processes
        for file_id in file_ids:
            file_data = files[file_id]
            associationIds = file_data['associationIds']
            match = filter(lambda x: x in associationIds, process_uuids)
            if match:
                process_uuid = match[0]
                processes[process_uuid]['files'].append(file_data)
            else:
                unmatched_files.append(file_data)

        # match processes to specimens
        for process_uuid in process_uuids:
            process = processes[process_uuid]
            associationIds = process['associationIds']

            match = filter(lambda x: x in associationIds, specimen_uuids)
            if match:
                specimen_uuid = match[0]
                specimens[specimen_uuid]['processes'].append(process)
            else:
                unmatched_processes.append(process)

        # stick specimens into project
        for specimen_uuid in specimen_uuids:
            specimen = specimens[specimen_uuid]
            project['specimens'].append(specimen)

        context = {'project' : project,
                   'specimen_count' : len(specimens),
                   'process_count' : len(processes),
                   'file_count' : len(files)}

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

        context = {'form': ProjectForm(), 'project': None}
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

            a = client(request)

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
def edit(request, project_uuid):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = client(request)
        try:
            project = a.meta.getMetadata(uuid=project_uuid)
        except:
            logger.error('Error while attempting to edit project, not found.')
            messages.error(request, 'Project not found.')
            return HttpResponseRedirect('/projects/')
        else:
            context = {'form': ProjectForm(initial=project),
                       'project': project}
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

            a = client(request)
            try:
                response = a.meta.updateMetadata(uuid=project_uuid, body=new_project)
            except Exception as e:
                logger.error('Error while attempting to edit project metadata.')
                messages.error(request, 'Error while attempting to edit specimen.')
                return HttpResponseRedirect('/projects/')
            else:
                messages.success(request, 'Successfully edited project.')
                return HttpResponseRedirect('/project/{}'.format(project_uuid))

        messages.success(request, 'Did not edit project.')
        return HttpResponseRedirect('/project/{}'.format(project_uuid))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def delete(request, project_uuid):
    """Delete a project """
    #######
    # GET #
    #######
    if request.method == 'GET':

        # TODO: ask user if they want to delete associated objects?

        a = client(request)

        # find all associated objects
        query = {'associationIds':'{}'.format(project_uuid)}
        results = a.meta.listMetadata(q=json.dumps(query))

        # delete all associated objects
        for result in results:
            a.meta.deleteMetadata(uuid=result.uuid)

        # delete project
        try:
            a.meta.deleteMetadata(uuid=project_uuid)
        except:
            logger.error('Error deleting project. {} {}'.format(e.errno, e.strerror) )
            messages.error(request, 'Project deletion unsuccessful.')

            return HttpResponseRedirect('/projects/')
        else:
            messages.success(request, 'Successfully deleted project.')
            return HttpResponseRedirect('/projects/')

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")
