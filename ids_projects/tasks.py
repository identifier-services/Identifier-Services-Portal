from __future__ import absolute_import

from celery import shared_task
from .models import Specimen, Project
from ids.utils import get_portal_api_client
from agavepy.agave import Agave                      
import os


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task(bind=True)
def bulk_specimen_registration(self, specimens_meta, project_uuid):
    # bad data?              
    # api_server = os.environ.get('AGAVE_TENANT_BASEURL', 'https://agave.iplantc.org/')
    # super_token = os.environ.get('AGAVE_SUPER_TOKEN')
    
    # api_client = Agave(api_server=api_server, token=super_token)
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