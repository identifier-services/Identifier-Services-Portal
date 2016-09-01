from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import logging
from ..forms.datasets import DatasetForm, DataSelectForm
from ..models import Project, Specimen, Process, Dataset, Data, Identifier
from ids.utils import (get_portal_api_client,
                       get_process_type_keys,
                       get_dataset_fields)
from requests import HTTPError
import urllib

logger = logging.getLogger(__name__)



@require_http_methods(['GET'])
def view(request, identifier_uuid):
    """View a specific identifier"""
    if request.user.is_anonymous():
        api_client = get_portal_api_client()
    else:
        api_client = request.user.agave_oauth.api_client

    try:
        identifier = Identifier(api_client=api_client, uuid=identifier_uuid)        
    except Exception as e:
        exception_msg = 'Unable to load process. %s' % e
        logger.error(exception_msg)
        messages.warning(request, exception_msg)
        return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

    try:        
        uid = identifier.uid
    except Exception as e:
        exception_msg = 'Unable to load config values. %s' % e
        logger.warning(exception_msg)

    url = "http://ezid.cdlib.org/id/" + uid
    
    return HttpResponseRedirect(url)