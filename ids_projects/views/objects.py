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
from ..models.specimen import Specimen
from ..models.process import Process
from ..models.dataset import Dataset
from ..models.data import Data


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



# /test/project_api/3176432264224379366-242ac1111-0001-012
@login_required
@require_http_methods(['GET'])
def project_api(request, project_uuid):
	print "project id %s" % project_uuid

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

		# pprint.pprint(response)

		return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), 
												content_type='application/json')

	except Exception as e:
		exception_msg = 'Unable to load project related objects. %s' % e
        logger.error(exception_msg)
        messages.error(request, exception_msg)
        return HttpResponseRedirect('/projects/')

# /test/specimen_api/1862119081942979046-242ac1111-0001-012
@login_required
@require_http_methods(['GET'])
def specimen_api(request, specimen_uuid):
	print "specimen id: %s" % specimen_uuid

	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client	

	specimen = Specimen(api_client=api_client, uuid=specimen_uuid)

	try:
		processes = specimen.processes

		response = {}
		response['is_input_of'] = []
		response['is_output_of'] = []

		for process in processes:
			response['is_input_of'].append({"title": process.title, "uuid": process.uuid})

		pprint.pprint(response)

		return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder),
												content_type='application/json')

	except Exception as e:
		exception_msg = 'Unable to load specimen related objects. %s' % e
		logger.error(exception_msg)
		messages.error(request, exception_msg)
		return HttpResponseRedirect('/projects/')



# /test/process_api/8000958787788739046-242ac1111-0001-012
@login_required
@require_http_methods(['GET'])
def process_api(request, process_uuid):
	print "process id: %s" % process_uuid
	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client

	process = Process(api_client=api_client, uuid=process_uuid)

	try:
		inputs = process.inputs
		outputs = process.outputs

		response = {}
		response['inputs'] = []
		response['outputs'] = []

		for entity in inputs:
			response['inputs'].append({"title": entity.title, "uuid": entity.uuid})

		for entity in outputs:
			response['outputs'].append({"title": entity.title, "uuid": entity.uuid})

		return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder),
												content_type='application/json')

	except Exception as e:
		exception_msg = 'Unable to load process related objects. %s' % e
		logger.error(exception_msg)
		messages.error(request, exception_msg)
		return HttpResponseRedirect('/projects')


# /test/dataset_api/2512897196004601370-242ac1111-0001-012
@login_required
@require_http_methods(['GET'])
def dataset_api(request, dataset_uuid):
	print "dataset id: %s" % dataset_uuid
	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client

	dataset = Dataset(api_client=api_client, uuid=dataset_uuid)

	try:
		identifiers = dataset.identifiers
		data = dataset.data

		response = {}
		response['identifiers'] = []
		response['data'] = []

		for identifier in identifiers:
			response['identifiers'].append({"title": identifier.title, "uuid": identifier.uuid})

		for dat in data:
			response['data'].append({"title": dat.title, "uuid": dat.uuid})

		return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder),
												content_type='application/json')

	except Exception as e:
		exception_msg = 'Unable to load dataset related objects. %s' % e
		logger.error(exception_msg)
		messages.error(request, exception_msg)
		return HttpResponseRedirect('/projects')

# /test/data_api/4322106814629932570-242ac1111-0001-012
@login_required
@require_http_methods(['GET'])
def data_api(request, data_uuid):
	print "data id: %s" % data_uuid
	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client

	data = Data(api_client=api_client, uuid=data_uuid)

	try:
		is_input_to = data.input_to_process
		is_output_of = data.output_of_process

		print is_input_to
		print is_output_of

		response = {}
		response['is_input_to'] = []
		response['is_output_of'] = []

		for process in is_input_to:
			response['is_input_to'].append({"title": process.title, "uuid": process.uuid})

		for process in is_output_of:
			response['is_output_of'].append({"title": process.title, "uuid": process.uuid})

		return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder),
												content_type='application/json')

	except Exception as e:
		exception_msg = 'Unable to load data related objects. %s' % e
		logger.error(exception_msg)
		messages.error(request, exception_msg)
		return HttpResponseRedirect('/projects')


	



