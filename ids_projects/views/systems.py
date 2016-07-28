from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import logging
from ..models import System

logger = logging.getLogger(__name__)


@login_required
def list(request):
    system_type = request.GET.get('type', None)
    if system_type:
        systems = System().list(system_type=system_type)
    else:
        systems = System().list()
    return JsonResponse([system.body for system in systems], safe=False)
