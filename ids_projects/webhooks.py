from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from models import Data
from ids.utils import get_portal_api_client
import logging
import datetime

logger = logging.getLogger(__name__)


@csrf_exempt
def handle_webhook(request, hook_type, *args, **kwargs):
    """
    Required parameters:
        hook_type           ['update_checksum'|'test_job']
        UUID                Unique IDS identifier for the data object to modify
        checksum            Calculated checksum value

    Testing from command line:
        curl -k --data 'UUID=2483901498122179046-242ac1111-0001-012&checksum=060a735c8f6240949ae7ac9fd8d22129' http://localhost:8000/webhook/update_checksum/
    """

    if hook_type == 'update_checksum':
        api_client = get_portal_api_client()

        try:
            logger.debug('profile: {}'.format(api_client.profiles.get()))
        except Exception as e:
            logger.error('bad client: %s', repr(e))

        logger.debug('Webhook request type: %s, body: %s' % (hook_type, request.body))

        if request.GET:
            print "GET"
            uuid = request.GET.get('UUID', None)
            checksum = request.GET.get('checksum', None)
            # last_checksum_update = request.GET.get('lastChecksumUpdated', None)
        elif request.POST:
            print "POST"
            logger.debug(request.POST)
            uuid = request.POST.get('UUID', None)
            checksum = request.POST.get('checksum', None)
            # last_checksum_update = request.POST.get('lastChecksumUpdated', None)

        if uuid is None:
            logger.exception('Missing UUID.')
            return HttpResponse("Error\n")

        if checksum is None:
            logger.exception('Missing checksum.')
            return HttpResponse("Error\n")

        try:
            data = Data(api_client=api_client, uuid=uuid)
            logger.debug('Metadata for UUID %s: %s' % (uuid, data.value))
        except Exception as e:
            logger.exception('Invalid UUID ( %s ), Agave object not found. %s' % (uuid, repr(e)))
            return HttpResponse("Error")

        updated_time = datetime.datetime.now()
        previous_checksum = data.value.get('checksum', None)

        time_template = "%Y-%m-%dT%H:%M:%S"

        if previous_checksum is None:
            try:
                data.value['checksum'] = checksum
                data.value['lastChecksumUpdated'] = updated_time.strftime(time_template)
                data.value['checkStatus'] = True
                data.save()
                logger.debug('New checksum saved for UUID: %s!' % uuid)
            except Exception as e:
                logger.exception('Checksum was not saved successfully. %s' % e)
                return HttpResponse("Error")
        elif previous_checksum == checksum:
            try:
                data.value['checksum'] = checksum
                data.value['lastChecksumUpdated'] = updated_time.strftime(time_template)
                data.value['checkStatus'] = True
                data.save()
                logger.debug('Checksum is identical, timestamp updated for UUID: %s!' % uuid)
            except Exception as e:
                logger.exception('Checksum was not saved successfully. %s' % e)
                return HttpResponse("Error")
        else:
            try:
                data.value['checksumConflict'] = checksum
                data.value['lastChecksumUpdated'] = updated_time.strftime(time_template)
                data.value['checkStatus'] = False
                data.save()
                logger.warning('Checksum is NOT consistent with previous for UUID: %s!' % uuid)
            except Exception as e:
                logger.exception('Checksum was not saved successfully. %s' % e)
                return HttpResponse("Error")

        return HttpResponse(uuid + ' ' + checksum + '\n')

    # testing for calling job
    elif hook_type == 'test_job':
        uuid = '4544798190901268966-242ac1111-0001-012'
        data = Data(uuid=uuid)
        data.calculate_checksum()
        return HttpResponse('Job submitted for uuid = %s!' % uuid)
    else:
        return HttpResponse('OK')
