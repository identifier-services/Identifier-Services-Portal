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
def files_list(request, system_id, file_path=''):
    a = client(request)
    listing = a.files.list(systemId=system_id, filePath=file_path)
    return JsonResponse(listing, safe=False)


@login_required
def add_data(request, dataset_id):
    a = client(request)

    context = {
        'dataset': a.meta.getMetadata(uuid=dataset_id),
        'systems': a.systems.list(type='STORAGE'),
    }

    return render(request, 'ids_datasets/add_data.html', context)
