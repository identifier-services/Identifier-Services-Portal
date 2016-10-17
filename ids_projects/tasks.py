from __future__ import absolute_import

from celery import shared_task
from .models import Specimen, Project, Probe, Process
from ids.utils import get_portal_api_client
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def bulk_specimen_registration(self, specimens_meta, project_uuid):        
    api_client = get_portal_api_client()
    project = Project(api_client=api_client, uuid=project_uuid)

    for specimen_info in specimens_meta:
        meta = {'value': specimen_info}
        specimen = Specimen(api_client=api_client, meta=meta)
        specimen.save()

        logger.debug("Specimen UUID: {}".format(specimen.uuid))

        # add_part: specimen
        project.add_specimen(specimen)
        project.save()

        # add_container: project
        specimen.add_project(project)
        specimen.save()            


@shared_task(bind=True)
def bulk_probe_registration(self, probes_meta, project_uuid):    
    api_client = get_portal_api_client()
    project = Project(api_client, uuid=project_uuid)

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
def bulk_ISH_registration(self, ISH_meta, process_meta, project_uuid):    
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
        probe_ids = ISH_link['probe_id'].split(',')

        logger.debug("Probe IDs: {}".format(probe_ids))
        probes = project.query_probes_by_id(probe_ids)

        for probe in probes:
            process.add_input(probe)
            probe.add_is_input_to(process)
            process.save()
            probe.save()
            # print probe.value

        # Query specimens with given specimen ids
        specimen_ids = ISH_link['specimen_id'].split(',')

        logger.debug("Specimen IDs: {}".format(specimen_ids))
        specimens = project.query_specimens_by_id(specimen_ids)

        for specimen in specimens:
            process.add_input(specimen)
            specimen.add_is_input_to(process)
            process.save()
            specimen.save()

        logger.debug("Process ID: {}".format(process.uuid))




