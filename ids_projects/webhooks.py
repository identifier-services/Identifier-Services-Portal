from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from ids_projects.models import Data
import json


@csrf_exempt
def handle_webhook(request, type, *args, **kwargs):
    # do stuff

    if type == 'agave':
        data = json.loads(request.body)

        # meta = Data(uuid=data['uuid'])
        # meta.value['md5'] = data['md5']
        # meta.save()

        return HttpResponse(data['uuid'] + ' ' + data['md5'])

    return HttpResponse('OK')
