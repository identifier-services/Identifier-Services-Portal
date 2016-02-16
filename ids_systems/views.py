from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse,
                         Http404, HttpResponseNotAllowed)
from agavepy.agave import Agave, AgaveException
import json, logging
from forms import SystemForm

logger = logging.getLogger(__name__)

from django.shortcuts import render

def _client(request):
    token = request.session.get(getattr(settings, 'AGAVE_TOKEN_SESSION_ID'))
    access_token = token.get('access_token', None)
    url = getattr(settings, 'AGAVE_TENANT_BASEURL')
    return Agave(api_server = url, token = access_token)

@login_required
def create(request, parent_id):
    pass

def detail(request, data_id):
    pass

@login_required
def edit(request, data_id):
    pass

@login_required
def delete(request, data_id):
    pass

@login_required
def index(request):
    a = _client(request)
    systems = a.systems.list(type='STORAGE')
    system_choices = []
    for system in systems:

        choice_tuple = (system.id,system.name)
        system_choices.append(choice_tuple)

    if request.method == 'POST':

        form = SystemForm(request.POST, systems=system_choices)

        if form.is_valid():
            choice = form.cleaned_data['system']
            return HttpResponseRedirect('/data/{}/list'.format(choice))
    else:
        return render(request, 'ids_systems/index.html',
            {
                'form':SystemForm(systems=system_choices)
            }
        )
