from agavepy.agave import Agave, AgaveException
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import (HttpResponse,
                         HttpResponseRedirect,
                         HttpResponseBadRequest,
                         HttpResponseForbidden,
                         HttpResponseNotFound,
                         HttpResponseServerError)
from django.shortcuts import render
import json, logging
from ..forms.projects import ProjectForm
from helper import client, collapse_meta


logger = logging.getLogger(__name__)


@login_required
def systems_list(request):
    a = _client(request)
    systems = a.systems.list(type='STORAGE')
    return JsonResponse(systems, safe=False)
