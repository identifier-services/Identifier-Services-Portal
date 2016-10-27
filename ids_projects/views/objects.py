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

import json
import logging

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