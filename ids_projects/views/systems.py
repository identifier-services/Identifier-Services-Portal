from agavepy.agave import Agave, AgaveException
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import (JsonResponse,
                         HttpResponse,
                         HttpResponseRedirect,
                         HttpResponseBadRequest,
                         HttpResponseForbidden,
                         HttpResponseNotFound,
                         HttpResponseServerError)
from django.shortcuts import render
import json, logging
#TODO: import system form
from ..forms.projects import ProjectForm
from ..models import System


logger = logging.getLogger(__name__)


@login_required
def list(request):
    system_type = request.GET.get('type', None)
    if system_type:
        systems = System().list(system_type=system_type)
    else:
        systems = System().list()
    return JsonResponse(systems, safe=False)

@login_required
def view(request, system_id):
    system = System(system_id=system_id)
    return JsonResponse(system.body, safe=False)

@login_required
def create(request):
    return HttpResponse(NotImplemented)

@login_required
def edit(request, system_id):
    return HttpResponse(NotImplemented)

@login_required
def delete(request, system_id):
    system = System(system_id=system_id)
    result = system.delete()
    return HttpResponse(result)
