from django.conf import settings
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from agavepy.agave import Agave, AgaveException
import json
import logging
import requests
import traceback

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(['GET'])
def public_projects(request, file_path = '/'):
    l = '{ 'message': 'public projects' }'
    return HttpResponse(json.dumps(l), content_type="application/json", status=200)

@login_required
@require_http_methods(['GET'])
def private_projects(request, file_path = '/'):
    l = '{ "message": "private projects" }'
    return HttpResponse(json.dumps(l), content_type="application/json", status=200)
