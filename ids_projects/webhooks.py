from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from ids_projects.models import Data
from django.conf import settings
from agavepy.agave import Agave
import json
import datetime


@csrf_exempt
def handle_webhook(request, type, *args, **kwargs):

    if type == 'agave':
        print request.body
        data = json.loads(request.body)        
        uuid = data['UUID']
        checksum = data['checksum']

        print uuid
        ag = Agave(api_server=settings.AGAVE_TENANT_BASEURL,token=settings.AGAVE_SUPER_TOKEN)

        try:
        	response = ag.meta.getMetadata(uuid=uuid)        	
       	except Exception as e:
         	response = None
        	print "Invalid UUID, Agave object not found."
        	return HttpResponse("Error")
                                        
        if response != None:
        	updated_time = datetime.datetime.now()
        	print updated_time
	        meta = Data(uuid=uuid)

	        # if checksum exists or matchs
	        if 'checksum' not in meta.value:
	        	meta.value['checksum'] = checksum
	        	meta.value['lastChecksumUpdated'] = updated_time.strftime("%Y-%m-%dT%H:%M:%S")
	        	meta.save()
	        elif meta.value['checksum'] == checksum:
	        	print "Checksum is updated successfully!"
	        	meta.value['lastChecksumUpdated'] = updated_time.strftime("%Y-%m-%dT%H:%M:%S")
	        	meta.save()
	        else:
	        	print "Checksum is NOT consistent with previous one!"
					        	        
        return HttpResponse(uuid + ' ' + checksum + '\n')

    # testing for calling job
    elif type == 'job':
        uuid = '4544798190901268966-242ac1111-0001-012'
        meta = Data(uuid = uuid)
        meta.calculate_checksum()
        return HttpResponse('Job submitted for uuid = %s!' % uuid)
    else:
        return HttpResponse('OK')

    
# testing command
# curl -k --data '{"UUID":"4544798190901268966-242ac1111-0001-012","checksum":"060a735c8f6240949ae7ac9fd8d22129"}' http://localhost:8000/webhook/agave/

