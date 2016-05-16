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
from ..models import Project, Specimen
from helper import client, collapse_meta
from requests import HTTPError


logger = logging.getLogger(__name__)


@login_required
def list(request):
    """List all specimens related to a project"""
    #######
    # GET #
    #######
    if request.method == 'GET':

        project_uuid = request.GET.get('project_uuid', None)
        project = Project(uuid = project_uuid, user=request.user)
        context = {'project': project, 'specimens' : project.specimens}
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

        specimen = Specimen(uuid = specimen_uuid)
        project = specimen.project

        context = {'project' : project, 'specimen' : specimen}

        return render(request, 'ids_projects/specimens/detail.html', context)

    #########
    # OTHER #
    #########
    else:
        django.http.HttpResponseNotAllowed("Method not allowed")


@login_required
def create(request):
    """Create a new specimen related to a project"""
    project_uuid = request.GET.get('project_uuid', False)

    #######
    # GET #
    #######
    if request.method == 'GET':

        if not project_uuid:
            messages.error(request, 'No project uuid')
            return HttpResponseRedirect(reverse('ids_projects:project-list'))

        project = Project(uuid=project_uuid, user=request.user)

        context = {'form_specimen_create': SpecimenForm(),
                   'project': project,
                   'specimen': None}

        return render(request, 'ids_projects/specimens/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = SpecimenForm(request.POST)

        if form.is_valid():

            # TODO: for some reason the project_uuid looks like it's actually the uuid for a specimen
            body = { 'associationIds':[project_uuid],
                     'value':form.cleaned_data }

            try:
                specimen = Specimen(initial_data = body)
                result = specimen.save()
                if not 'uuid' in result:
                    raise Exception('Invalid API response: {}.'.format(result))
                specimen_uuid = result['uuid']
                success_msg = 'Successfully created specimen.'
                logger.debug(success_msg)
                messages.success(request, success_msg)
                return HttpResponseRedirect(
                            reverse('ids_projects:specimen-view',
                                    kwargs={'specimen_uuid': specimen_uuid}))
            except HTTPError as e:
                logger.debug('Error while attempting to create specimen metadata: %s' % e)
            except Exception as e:
                logger.debug('Error while attempting to create specimen metadata: %s' % e)

        # execution falls through to here if an exception is caught, or the form is not valid
        messages.error(request, 'Encountered error while creating new Specimen.')
        return HttpResponseRedirect(
                        reverse('ids_projects:project-view',
                            kwargs={'project_uuid': project_uuid}))

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

            context = {'form_specimen_edit': SpecimenForm(initial=specimen),
                       'specimen': specimen,
                       'project': project}
            return render(request, 'ids_projects/specimens/create.html', context)

    ########
    # POST #
    ########
    elif request.method == 'POST':

        form = SpecimenForm(request.POST)

        # get the association fields
        a = client(request)
        try:
            # get the specimen metadata object
            specimen_raw = a.meta.getMetadata(uuid=specimen_uuid)
            specimen = collapse_meta(specimen_raw)
        except Exception as e:
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
