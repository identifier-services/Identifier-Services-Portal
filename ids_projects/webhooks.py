from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from ids_projects.models import Data
from django.conf import settings
from agavepy.agave import Agave
import json, logging, datetime

logger = logging.getLogger(__name__)


@csrf_exempt
def handle_webhook(request, hook_type, *args, **kwargs):
    # testing command
    # curl -k --data '{"UUID":"4544798190901268966-242ac1111-0001-012","checksum":"060a735c8f6240949ae7ac9fd8d22129"}' http://localhost:8000/webhook/update_checksum/
    if hook_type == 'update_checksum':
        logger.debug('Webhook request type: %s, body: %s' % (hook_type, request.body))

        data = json.loads(request.body)
        uuid = data['UUID']
        checksum = data['checksum']

        try:
            meta = Data(uuid=uuid, public=False)
            logger.debug('Metadata for UUID %s: %s' % (uuid, meta.body))
        except Exception as e:
            logger.exception('Invalid UUID ( %s ), Agave object not found.' % uuid)
            return HttpResponse("Error")

        updated_time = datetime.datetime.now()
        previous_checksum = meta.value.get('checksum', None)

        if previous_checksum is None:
            try:
            	meta.value['checksum'] = checksum
            	meta.value['lastChecksumUpdated'] = updated_time.strftime("%Y-%m-%dT%H:%M:%S")
            	meta.save()
                logger.debug('New checksum saved for UUID: %s!' % uuid)
            except Exception as e:
                logger.exception('Checksum was not saved successfully. %s' % e)
                return HttpResponse("Error")
        elif previous_checksum == checksum:
            try:
            	meta.value['checksum'] = checksum
            	meta.value['lastChecksumUpdated'] = updated_time.strftime("%Y-%m-%dT%H:%M:%S")
            	meta.save()
                logger.debug('Checksum is identical, timestamp updated for UUID: %s!' % uuid)
            except Exception as e:
                logger.exception('Checksum was not saved successfully. %s' % e)
                return HttpResponse("Error")
        else:
            try:
                meta.value['checksum_conflict'] = checksum
            	meta.value['lastChecksumUpdated'] = updated_time.strftime("%Y-%m-%dT%H:%M:%S")
            	meta.save()
                logger.warning('Checksum is NOT consistent with previous for UUID: %s!' % uuid)
            except Exception as e:
                logger.exception('Checksum was not saved successfully. %s' % e)
                return HttpResponse("Error")

        return HttpResponse(uuid + ' ' + checksum + '\n')

    # testing for calling job
    elif hook_type == 'test_job':
        uuid = '4544798190901268966-242ac1111-0001-012'
        meta = Data(uuid = uuid)
        meta.calculate_checksum()
        return HttpResponse('Job submitted for uuid = %s!' % uuid)
    else:
        return HttpResponse('OK')
