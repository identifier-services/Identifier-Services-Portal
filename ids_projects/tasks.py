from __future__ import absolute_import

from celery import shared_task
from .models import Specimen, Project, Probe
from ids.utils import get_portal_api_client
from agavepy.agave import Agave                      

import os

@shared_task(bind=True)
def bulk_specimen_registration(self, specimens_meta, project_uuid):        
    api_client = get_portal_api_client()
    project = Project(api_client=api_client, uuid=project_uuid)

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
def bulk_probe_registration(self, probes_meta, project_uuid):    
    print "in the task call"
    api_client = get_portal_api_client()
    project = Project(api_client, uuid=project_uuid)

    count = 0
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

        count  = count + 1
        print "# of probes: " % count