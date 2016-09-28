from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# from ..forms.specimens import SpecimenForm
from ..models import Project
from ids.utils import (get_portal_api_client,
                       get_process_type_keys)

from ..forms.upload_option import UploadOptionForm, UploadFileForm

import logging
import csv
import traceback

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET','POST'])
def upload_option(request):
	
	project_uuid = request.GET.get('project_uuid', False)
	print project_uuid

	if not project_uuid:
		message.warning(request, 'Missing project UUID, cannot create probe.')
		return HttpResponseRedirect(reverse('ids_projects:project-list-private'))    
	
	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client

	project = Project(api_client=api_client, uuid=project_uuid)

	# POST
	if request.method == 'POST':
		context = {'project': project}

		if request.POST.get('upload_option', None) == 'Single':
			return HttpResponseRedirect(
                            reverse('ids_projects:project-view',
                                    kwargs={'project_uuid': project.uuid}))

        elif request.POST.get('upload_option', None) == 'Bulk':

        	try:
        		print "in the function"
        		probes_meta = _validate_probes(request.FILES['file'], project)

        		print "out"
        		# use celery to process probe registration

        		# success_msg = 'Your %d probes have been in the registration queue.' % len(probes_meta)
          #       logger.info(success_msg)
          #       messages.success(request, success_msg)

        	except Exception as e:
				traceback.print_exc()
                exception_msg = repr(e)
                logger.error(exception_msg) 
                messages.warning(request, exception_msg)            	
            	return HttpResponseRedirect(reverse('ids_projects:project-list-private'))

	else:
		context = {'project': project}
		context['form_upload_file'] = UploadFileForm()
		context['form_upload_option'] = UploadOptionForm()
		return render(request, 'ids_projects/probes/upload_option.html', context)
	

def _validate_probes(f, project):
	header = True
	row_num = 0
	probes_meta = []

	probe_fields = get_probe_fields(project)
	reader = csv.reader(f)
	
	if header:
		next(reader, None)

	for row in reader:	
		meta = {}
		col_num = 0
		for field in probe_fields[:-1]:
			meta[field['id']] = row[col_num]
			col_num = col_num + 1

		probes_meta.append(meta)
		row_num = row_num + 1

	print probes_meta
	return probes_meta