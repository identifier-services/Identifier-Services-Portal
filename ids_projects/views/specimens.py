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
from ..forms.specimens import SpecimenForm
from helper import client, collapse_meta


logger = logging.getLogger(__name__)


@login_required
# def list(request, project_uuid):
def list(request):
    """List all specimens related to a project"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        project_uuid = request.GET.get('project_uuid', False)

        a = client(request)
        if project_uuid:
            specimens_query = {'name':'idsvc.specimen','associationIds':'{}'.format(project_uuid)}
        else:
            specimens_query = {'name':'idsvc.specimen'}

        print(specimens_query)

        specimens_raw = a.meta.listMetadata(q=json.dumps(specimens_query))
        specimens = map(collapse_meta, specimens_raw)

        if project_uuid:
            project_raw = a.meta.getMetadata(uuid=project_uuid)
            project = collapse_meta(project_raw)
        else:
            project = None

        context = {'specimens' : specimens, 'project': project}

        return render(request, 'ids_projects/specimens/index.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def view(request, specimen_uuid):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        # get specimen metadata
        a = client(request)
        specimen_raw = a.meta.getMetadata(uuid=specimen_uuid)
        specimen = collapse_meta(specimen_raw)

        project = None

        # find the project that the specimen is associated with
        associationIds = specimen['associationIds']
        query = {'uuid': { '$in': associationIds }}
        results_raw = a.meta.listMetadata(q=json.dumps(query))
        results = map(collapse_meta, results_raw)
        for result in results:
            if result['name'] == 'idsvc.project':
                project = result

        # get all objects with specimen_uuid in associationIds list
        query = {'associationIds': specimen_uuid }
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
        process_uuids = processes.keys()
        file_ids = files.keys()

        # place to put objects that were created 'out of order'
        unmatched_processes = []
        unmatched_files = []

        # match files with processes
        for file_id in file_ids:
            file_data = files[file_id]
            associationIds = file_data['associationIds']
            match = filter(lambda x: x in associationIds, process_uuids)
            if match:
                process_uuid = match[0]
                processes[process_uuid]['files'].append(file_data)
            else:
                unmatched_files.append(file_data)

        # list to hold the specimen's processes
        specimen['processes'] = []

        # stick processes into specimen
        for process_uuid in process_uuids:
            process = processes[process_uuid]
            specimen['processes'].append(process)

        context = {'specimen' : specimen, 'project' : project}

        return render(request, 'ids_projects/specimens/detail.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def create(request):
    """Create a new specimen related to a project"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        project_uuid = request.GET.get('project_uuid', False)

        if not project_uuid:
            messages.error(request, 'No project uuid')
            return HttpResponseRedirect(reverse('ids_projects:specimens-list'))

        # get the project
        a = client(request)
        project_raw = a.meta.getMetadata(uuid=project_uuid)
        project = collapse_meta(project_raw)

        context = {'form': SpecimenForm(),
                   'project': project,
                   'specimen': None}

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

            associationIds = [project_uuid]

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
        return HttpResponseRedirect('/project/{}'.format(project_uuid))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def edit(request, specimen_uuid):
    """ """
    #######
    # GET #
    #######
    if request.method == 'GET':

        a = client(request)
        try:
            # get the specimen metadata object
            specimens_raw= a.meta.getMetadata(uuid=specimen_uuid)
            specimen = collapse_meta(specimens_raw)
        except Exception as e:
            logger.error('Error editing specimen. {}'.format(e.message))
            messages.error(request, 'Specimen not found.')

            return HttpResponseRedirect('/projects/')
        else:
            # find the project that the specimen is associated with
            project = None
            associationIds = specimen['associationIds']
            query = {'uuid': { '$in': associationIds }}
            results_raw = a.meta.listMetadata(q=json.dumps(query))
            results = map(collapse_meta, results_raw)
            for result in results:
                if result['name'] == 'idsvc.project':
                    project = result

            context = {'form': SpecimenForm(initial=specimen),
                       'specimen': specimen,
                       'project': project}
            return render(request, 'ids_projects/specimens/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = SpecimenForm(request.POST)

        # get the association fields
        # TODO: I need to store this in hidden form field, but having trouble with that.
        a = client(request)
        try:
            # get the specimen metadata object
            specimen_raw= a.meta.getMetadata(uuid=specimen_uuid)
            specimen = collapse_meta(specimens_raw)
        except:
            logger.error('Error editing specimen. {}'.format(e.message))
            messages.error(request, 'Specimen not found.')

            return HttpResponseRedirect('/projects/')
        else:
            associationIds = specimen['associationIds']

        if form.is_valid():

            taxon_name = form.cleaned_data['taxon_name']
            specimen_id = form.cleaned_data['specimen_id']
            organ_or_tissue = form.cleaned_data['organ_or_tissue']
            developmental_stage = form.cleaned_data['developmental_stage']
            haploid_chromosome_count = form.cleaned_data['haploid_chromosome_count']
            ploidy = form.cleaned_data['ploidy']
            propagation = form.cleaned_data['propagation']
            estimated_genome_size = form.cleaned_data['estimated_genome_size']

            new_specimen = {
                "name" : 'idsvc.specimen',
                "associationIds" : associationIds,
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
                response = a.meta.updateMetadata(uuid=specimen_uuid, body=new_specimen)
            except Exception as e:
                logger.debug('Error while attempting to edit specimen metadata: %s' % e)
                messages.error(request, 'Error while attempting to edit specimen.')
            else:
                messages.success(request, 'Successfully edited specimen.')
                return HttpResponseRedirect('/specimen/{}'.format(specimen_uuid))

        messages.info(request, 'Did not edit specimen.')
        return HttpResponseRedirect('/specimen/{}'.format(specimen_uuid))

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def delete(request, specimen_uuid):
    """Delete a specimen"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        # TODO: Ask user if process and file data should be deleted

        # get the specimen
        a = client(request)
        specimen_raw = a.meta.getMetadata(uuid=specimen_uuid)
        specimen = collapse_meta(specimen_raw)

        project = None

        # find the project that the specimen is associated with
        associationIds = specimen['associationIds']
        query = {'uuid': { '$in': associationIds }}
        results_raw = a.meta.listMetadata(q=json.dumps(query))
        results = map(collapse_meta, results_raw)
        for result in results:
            if result['name'] == 'idsvc.project':
                project = result

        try:
            a.meta.deleteMetadata(uuid=specimen_uuid)
        except:
            logger.error('Error deleting specimen. {}'.format(e.message) )
            messages.error(request, 'Specimen deletion unsuccessful.')

            if project:
                return HttpResponseRedirect('/project/{}'.format(project['uuid']))
            else:
                return HttpResponseRedirect('/projects/')
        else:
            messages.success(request, 'Successfully deleted specimen.')

            if project:
                return HttpResponseRedirect('/project/{}'.format(project['uuid']))
            else:
                return HttpResponseRedirect('/projects/')

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")
