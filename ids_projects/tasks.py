from __future__ import absolute_import

from celery import shared_task
from .models import Specimen, Project, Probe, Process, Data
from ids.utils import get_portal_api_client
from agavepy.agave import Agave

import os

from django.contrib.auth import get_user_model

@shared_task(bind=True)
def bulk_specimen_registration(self, specimens_meta, project_uuid, username=None):

    if username:
        UserModel = get_user_model()
        user = UserModel.objects.get(username=username)
        api_client = user.agave_oauth.api_client
    else:
        api_client = get_portal_api_client()

    project = Project(api_client=api_client, uuid=project_uuid)

    # ## check if the specimen is already registered by the project
    # for specimen_info in specimens_meta:
    #     specimen_id = specimen_info['specimen_id']
    #     specimen = project.query_specimens_by_id([specimen_id]) # taking a list as input

    #     # already exists a speicmen
    #     if len(specimen) > 0:
    #         raise Exception('Specimen ID of %s already exists in this project.' % specimen_id)

    ## registering bulk specimens
    for specimen_info in specimens_meta:
        meta = {'value': specimen_info}
        specimen = Specimen(api_client=api_client, meta=meta)
        specimen.save()

        # add_part: specimen
        project.add_specimen(specimen)
        project.save()

        # add_container: project
        specimen.add_project(project)
        specimen.save()

@shared_task(bind=True)
def bulk_probe_registration(self, probes_meta, project_uuid, username=None):

    if username:
        UserModel = get_user_model()
        user = UserModel.objects.get(username=username)
        api_client = user.agave_oauth.api_client
    else:
        api_client = get_portal_api_client()

    project = Project(api_client, uuid=project_uuid)

    ## check if the probe is already registered by the project

    for probe_info in probes_meta:
        meta = {'value': probe_info}
        probe = Probe(api_client=api_client, meta=meta)
        probe.save()

        # add_part: probe
        project.add_probe(probe)
        project.save()

        # add_container: project
        probe.add_project(project)
        probe.save()


@shared_task(bind=True)
def bulk_ISH_registration(self, ISH_meta, process_meta, project_uuid, username=None):

    if username:
        UserModel = get_user_model()
        user = UserModel.objects.get(username=username)
        api_client = user.agave_oauth.api_client
    else:
        api_client = get_portal_api_client()

    project = Project(api_client, uuid=project_uuid)

    for ISH_link in ISH_meta:
        # create a new process
        process = Process(api_client=api_client, meta=process_meta)
        process.save()

        # two-way binding
        project.add_process(process)
        project.save()
        process.add_project(project)
        process.save()

        # Query probes with given probe ids
        # TO DO: What if some probes are not registered in the system
        probe_ids = ISH_link['probe_id'].split(',')
        probes = project.query_probes_by_id(probe_ids)

        # Query specimens with given specimen ids
        specimen_ids = ISH_link['specimen_id'].split(',')
        specimens = project.query_specimens_by_id(specimen_ids)

        # Query data with given image uri
        image_urls = ISH_link['image_url'].split(',')
        images = project.query_images_by_url(image_urls)
        print "number of images returned %d" % len(images)

        for probe in probes:
            process.add_input(probe)
            probe.add_is_input_to(process)
            process.save()
            probe.save()

        for specimen in specimens:
            process.add_input(specimen)
            specimen.add_is_input_to(process)
            process.save()
            specimen.save()

        for image in images:
            process.add_output(image)
            image.add_is_output_of(process)
            process.save()
            image.save()

        print "Process id: %s" % process.uuid

@shared_task(bind=True)
def bulk_images_registration(self, images_meta, project_uuid, username=None):

    if username:
        UserModel = get_user_model()
        user = UserModel.objects.get(username=username)
        api_client = user.agave_oauth.api_client
    else:
        api_client = get_portal_api_client()

    project = Project(api_client, uuid=project_uuid)

    for image_meta in images_meta:
        meta = {'value': image_meta}
        # create new data object
        data = Data(api_client=api_client, meta=meta)
        data.save()
        # data.calculate_checksum()

        project.add_data(data)
        project.save()

        data.add_project(project)
        data.save()
