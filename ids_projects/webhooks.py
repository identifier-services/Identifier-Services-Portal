from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
import json


@csrf_exempt
def handle_webhook(request, type, *args, **kwargs):
    # do stuff

    if type == 'agave':
        data = json.loads(request.body)

        return HttpResponse(data['uuid'] + ' ' + data['md5'])

    return HttpResponse('OK')
