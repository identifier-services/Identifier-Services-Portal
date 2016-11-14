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

# Examples
# /angular/project/2625065660983668250-242ac1111-0001-012
# /angular/project/3176432264224379366-242ac1111-0001-012
# /angular/data/4322106814629932570-242ac1111-0001-012
# /angular/dataset/2512897196004601370-242ac1111-0001-012
# /angular/probe/2842383520227267046-242ac1111-0001-012
# /angular/process/8000958787788739046-242ac1111-0001-012
# /angular/specimen/3539497870490791450-242ac1111-0001-012

@login_required
@require_http_methods(['GET'])
def view(request, uuid, entity):
	print "requesting %s with uuid = %s" % (entity, uuid)
	context = {'uuid': uuid, 'entityType': entity}
	return render(request, 'index.html', context)

# get entity detail
@login_required
@require_http_methods(['GET'])
def entity_detail_api(request, uuid):		
	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client	

   	base = BaseMetadata(api_client=api_client, uuid=uuid)
   	return HttpResponse(json.dumps(base.meta, cls=DjangoJSONEncoder),
   												content_type='application/json')


# get project's parts
# project with 800 probes
# /test/get_parts_api/idsvc.probe/2625065660983668250-242ac1111-0001-012/0

# project with probes, specimens, data, process
# /test/get_parts_api/idsvc.probe/3176432264224379366-242ac1111-0001-012/0
@login_required
@require_http_methods(['GET'])
def get_parts_api(request, name, uuid, offset):	
	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client	

	try:		
		query = {'name': name, 'value._relationships': {'$elemMatch': {'@id': uuid, '@rel:type': 'IsPartOf'}}}			
		response = api_client.meta.listMetadata(q=json.dumps(query), offset=offset)

		print "number of %s: %d" % (name, len(response))

		return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder),
												content_type='application/json')
	except Exception as e:
		exception_msg = 'Unable to load related objects. %s' % e
        logger.error(exception_msg)
        messages.error(request, exception_msg)
        return HttpResponseRedirect('/projects/')

# get process inputs
# /api/get_inputs/2842780581692314086-242ac1111-0001-012/0
@login_required
@require_http_methods(['GET'])
def get_inputs_api(request, uuid, offset):
	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client

	try:
		query = {'value._relationships': {'$elemMatch': {'@id': uuid, '@rel:type': 'IsInputTo'}}}
		response = api_client.meta.listMetadata(q=json.dumps(query), offset=offset)

		return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), 
												content_type='application/json')

	except Exception as e:
		exception_msg = 'Unable to load related objects. %s' % e
        logger.error(exception_msg)
        messages.error(request, exception_msg)
        return HttpResponseRedirect('/projects/')

# /api/get_outputs/2842780581692314086-242ac1111-0001-012/0
@login_required
@require_http_methods(['GET'])
def get_outputs_api(request, uuid, offset):
	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client

	try:
		query = {'value._relationships': {'$elemMatch': {'@id': uuid, '@rel:type': 'IsOutputOf'}}}
		response = api_client.meta.listMetadata(q=json.dumps(query), offset=offset)
		return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), 
												content_type='application/json')

	except Exception as e:
		exception_msg = 'Unable to load related objects. %s' % e
        logger.error(exception_msg)
        messages.error(request, exception_msg)
        return HttpResponseRedirect('/projects/')		

#/api/get_inputs_to/1825247573638311450-242ac1111-0001-012/0

@login_required
@require_http_methods(['GET'])
def get_inputs_to_api(request, uuid, offset):
	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client

	try:
		query = {'value._relationships': {'$elemMatch': {'@id': uuid, '@rel:type': 'HasInput'}}}
		response = api_client.meta.listMetadata(q=json.dumps(query), offset=offset)
		return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), 
												content_type='application/json')

	except Exception as e:
		exception_msg = 'Unable to load related objects. %s' % e
        logger.error(exception_msg)
        messages.error(request, exception_msg)
        return HttpResponseRedirect('/projects/')

# api/get_outpus_of/817918249993114086-242ac1111-0001-012/0
@login_required
@require_http_methods(['GET'])
def get_outputs_of_api(request, uuid, offset):
	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client

	try:
		query = {'value._relationships': {'$elemMatch': {'@id': uuid, '@rel:type': 'HasOutput'}}}
		response = api_client.meta.listMetadata(q=json.dumps(query), offset=offset)
		return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), 
												content_type='application/json')

	except Exception as e:
		exception_msg = 'Unable to load related objects. %s' % e
        logger.error(exception_msg)
        messages.error(request, exception_msg)
        return HttpResponseRedirect('/projects/')

