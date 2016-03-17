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
from ..forms.specimens import SpecimenForm
from helper import client, collapse_meta


logger = logging.getLogger(__name__)


@login_required
def list(request, project_id):
    """List all specimens related to a project"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = client(request)
        specimens_query = {'name':'idsvc.specimen','associationIds':'{}'.format(project_id)}
        specimens_raw = a.meta.listMetadata(q=json.dumps(specimens_query))
        specimens = map(collapse_meta, specimens_raw)

        context = {'specimens' : specimens, 'project_id': project_id}

        return render(request, 'ids_projects/specimens/index.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def view(request, specimen_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        # get specimen metadata
        a = client(request)
        specimen_raw = a.meta.getMetadata(uuid=specimen_id)
        specimen = collapse_meta(specimen_raw)

        # find project specimen is associated with
        associationIds = specimen['associationIds']
        query = {'associationIds': { '$in': associationIds }}
        results = a.meta.listMetadata(q=json.dumps(query))
        project_id = None
        for result in results:
            if result.name == 'idsvc.project':
                project_id == result.uuid

        # get all objects with specimen_id in associationIds list
        query = {'associationIds': specimen_id }
        results_raw = a.meta.listMetadata(q=json.dumps(query))
        results = map(collapse_meta, results_raw)

        # create dicts to group by type
        processes = {}
        files = {}

        # group by type
        for result in results:
            uuid = result['uuid']
            name = result['name']
            if name == 'idsvc.process':
                # let's make things clear, call the result a process
                process = result
                # create a list for file metadata
                process['files'] = []
                # add to dict
                processes[uuid] = process
            elif name == 'idsvc.data':
                # let's make things clear, call the result file_data
                file_data = result
                # add to dict
                files[uuid] = file_data

        # get the uuids
        process_ids = processes.keys()
        file_ids = files.keys()

        # place to put objects that were created 'out of order'
        unmatched_processes = []
        unmatched_files = []

        # match files with processes
        for file_id in file_ids:
            file_data = files[file_id]
            associationIds = file_data['associationIds']
            match = filter(lambda x: x in associationIds, process_ids)
            if match:
                process_id = match[0]
                processes[process_id]['files'].append(file_data)
            else:
                unmatched_files.append(file_data)

        # list to hold the specimen's processes
        specimen['processes'] = []

        # stick processes into specimen
        for process_id in process_ids:
            process = processes[process_id]
            specimen['processes'].append(process)

        context = {'specimen' : specimen, 'project_id' : project_id}

        return render(request, 'ids_projects/specimens/detail.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def create(request, project_id):
    """Create a new specimen related to a project"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        context = {'form': SpecimenForm(), 'project_id': project_id}

        return render(request, 'ids_projects/specimens/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = SpecimenForm(request.POST)

        if form.is_valid():

            taxon_name = form.cleaned_data['taxon_name']
            specimen_id = form.cleaned_data['specimen_id']
            organ_or_tissue = form.cleaned_data['organ_or_tissue']
            developmental_stage = form.cleaned_data['developmental_stage']
            haploid_chromosome_count = form.cleaned_data['haploid_chromosome_count']
            ploidy = form.cleaned_data['ploidy']
            propagation = form.cleaned_data['propagation']
            estimated_genome_size = form.cleaned_data['estimated_genome_size']

            associationIds = [project_id]

            new_specimen = {
                "name":"idsvc.specimen",
                "associationIds": associationIds,
                "value": {
                    "taxon_name":taxon_name,
                    "specimen_id":specimen_id,
                    "organ_or_tissue":organ_or_tissue,
                    "developmental_stage":developmental_stage,
                    "haploid_chromosome_count":haploid_chromosome_count,
                    "ploidy":ploidy,
                    "propagation":propagation,
                    "estimated_genome_size":estimated_genome_size,
                }
            }

            a = client(request)
            try:
                response = a.meta.addMetadata(body=new_specimen)
            except Exception as e:
                logger.debug('Error while attempting to create specimen metadata: %s' % e)
            else:
                messages.success(request, 'Successfully created specimen.')
                return HttpResponseRedirect('/specimen/{}'.format(response['uuid']))

        messages.info(request, 'Did not create new specimen.')
        return HttpResponseRedirect('/project/{}'.format(project_id))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def edit(request, specimen_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = client(request)
        query = {'uuid':project_id}
        project_list = a.meta.listMetadata(q=json.dumps(query))

        try:
            project = project_list[0]
        except:
            return HttpResponseNotFound("Project not found")
        else:
            return HttpResponse(json.dumps(project), content_type="application/json", status=200)

    ########
    # POST #
    ########
    elif request.method == 'POST':
        return HttpResponse("Creating new project: {}".format(len(projects)+1))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def delete(request, specimen_id):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = client(request)
        specimens_query = {
            'name':'idsvc.specimen',
            'associationIds':'{}'.format(project_id)
        }
        specimens_list = a.meta.listMetadata(q=json.dumps(specimens_query))

        return HttpResponse(json.dumps(specimens_list),
            content_type="application/json", status=200)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")
