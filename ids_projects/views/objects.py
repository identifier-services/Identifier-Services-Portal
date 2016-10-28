from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.core.serializers.json import DjangoJSONEncoder
from ids.utils import (get_portal_api_client,
                       get_process_type_keys,
                       get_project_form_fields,
                       get_investigation_type)

from ..models.base_metadata import BaseMetadata
from ..models.project import Project

import json
import logging
import pprint

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET'])
def test_angular(request):
    print "in the test angular"
    context = {}
    return render(request, 'index.html', context)


@login_required
@require_http_methods(['GET'])
def call_api(request, uuid):	
	print uuid

	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client	

   	base = BaseMetadata(api_client=api_client, uuid=uuid)
   	print base.value

   	return HttpResponse(json.dumps(base.value, cls=DjangoJSONEncoder),
   												content_type='application/json')



# test url: /test/api_project/3176432264224379366-242ac1111-0001-012
@login_required
@require_http_methods(['GET'])
def project_api(request, project_uuid):
	print project_uuid

	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client	

	project = Project(api_client=api_client, uuid=project_uuid)

	try:
		specimens = project.specimens
		probes = project.probes	
		processes = project.processes
		data = project.data
		datasets = project.datasets

		response = {}
		response['specimens'] = []
		response['probes'] = []
		response['processes'] = []
		response['data'] = []
		response['datasets'] = []

		for specimen in specimens:
			response['specimens'].append({"title": specimen.title, "uuid": specimen.uuid})

		for probe in probes:
			response['probes'].append({"title": probe.title, "uuid": probe.uuid})			

		for process in processes:
			response['processes'].append({"title": process.title, "uuid": process.uuid})

		for dat in data:
			response['data'].append({"title": dat.title, "uuid": dat.uuid})			

		for dataset in datasets:
			response['datasets'].append({"title": dataset.title, "uuid": dataset.uuid})

		pprint.pprint(response)

		return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), 
												content_type='application/json')

	except Exception as e:
		exception_msg = 'Unable to load project related objects. %s' % e
        logger.error(exception_msg)
        messages.error(request, exception_msg)
        return HttpResponseRedirect('/projects/')
	



