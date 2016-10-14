from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# from ..forms.specimens import SpecimenForm
from ..models import Project
from ids.utils import (get_portal_api_client,
                       get_process_type_keys,
                       get_probe_fields)

from ..forms.upload_option import UploadOptionForm, UploadFileForm

from ids_projects.tasks import bulk_probe_registration

import logging
import csv
import traceback
import pprint

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET','POST'])
def upload_option(request):	
	project_uuid = request.GET.get('project_uuid', False)	

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
		else:
			try:
				print request.POST.get('upload_option', None)
				probes_meta = _validate_probes(request.FILES['file'], project)				
				bulk_probe_registration.apply_async(args=(probes_meta,
															project_uuid), serializer='json')
				return HttpResponseRedirect(
								reverse('ids_projects:project-view',
										kwargs={'project_uuid': project.uuid}))

			except Exception as e:
				traceback.print_exc()
				exception_msg = repr(e)
				logger.error(exception_msg)
				messages.warning(request, exception_msg)

				return HttpResponseRedirect(
								reverse('ids_projects:project-view',
										kwargs={'project_uuid': project_uuid}))

    # GET
	else:
		print "GET method"
		context = {'project': project}
		context['form_upload_file'] = UploadFileForm()
		context['form_upload_option'] = UploadOptionForm()
		return render(request, 'ids_projects/probes/upload_option.html', context)
	

def _validate_probes(f, project):
	header = True
	row_num = 0
	probes_meta = []

	probe_fields = get_probe_fields(project)
	fields_length = len(probe_fields)
	
	reader = csv.reader(f)
	
	if header:
		row = next(reader, None)
		i = 0
		for index in range(fields_length):
			if row[index].lower() != probe_fields[index]['id']:				
				raise Exception("Fields does not match!")
			else:
				print "Field match OK: %s" % row[index]

	for row in reader:	
		meta = {}
		col_num = 0
		for field in probe_fields:
			meta[field['id']] = row[col_num]
			col_num = col_num + 1

		probes_meta.append(meta)
		row_num = row_num + 1

	# pprint.pprint(probes_meta[0])
	return probes_meta