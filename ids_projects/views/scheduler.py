from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.core.serializers.json import DjangoJSONEncoder
from ids.utils import get_portal_api_client

from ids_projects.tasks import bulk_checksum_verification

import logging
import requests
import httplib
from urlparse import urlparse

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET'])
def check(request):
	SRA = 'SRR1610960'
	check_SRA(SRA)

	external_url = "http://datacommons.cyverse.org/download/iplant/home/shared/commons_repo/curated/Duitama_rice_variation_2015/WGSOryza_CIAT_LSU_USDA_NCGR_SV/Esperanza_bowtie2_NGSEP_SV.gff"
	check_external_file(external_url)

	filePath = "mingchen7/others/WGSOryza_CIAT_LSU_USDA_NCGR_SV.tar.gz"
	system_id = "data.iplantcollaborative.org"
	check_agave_file(request, system_id, filePath)
	return HttpResponseRedirect('/')

def check_SRA(SRA):
	URL_prefix = 'https://www.ncbi.nlm.nih.gov/public/?/ftp/sra/sra-instant/reads/ByRun/sra/'
	SRA_prefix = SRA[0:3]
	prefix_accession = SRA[0:6]

	complete_url = URL_prefix + '/'.join([SRA_prefix, prefix_accession, SRA])
	print complete_url
	r = requests.get(complete_url)
	
	if r.status_code == 200:
		print "SRA file exists."
		return True
	else:
		print "Location check failed: SRA page does not exists"
		return False

def check_external_file(url):
	p = urlparse(url)
	conn = httplib.HTTPConnection(p.netloc)
	conn.request('HEAD', p.path)
	resp = conn.getresponse()

	if resp.status < 400:
		print "External file exists."
		return True
	else:
		print "Location check failed: external file does not exist."
		return False

def check_agave_file(request, system_id, file_url):
	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client	

	files = api_client.files.list(filePath=file_url, systemId=system_id)
	
	if files:
		print "File exists on agave."
		for f in files:
			print f.path

		return True			
	else:
		print "Location check failed: file does not exist on agave."
		return False


def dataste_integrity_check(request, uuid):
	if request.user.is_anonymous():
		api_client = get_portal_api_client()
	else:
		api_client = request.user.agave_oauth.api_client	

	dataset = Dataset(api_client, uuid=uuid)

	for dat in dataset.data:
		if dat.sra_id:
			resposne = check_SRA(dat.sra_id)
		else if dat.system_id:
			respsone = check_agave_file(request, dat.system_id, dat.path)
		else:
			resposne = check_external_file(dat.path)

		if not response:
			print "Location check failed: %s" % (dat.title)	
			return HttpResponseRedirect('/')

	bulk_checksum_verification.apply_async(args=(uuid,                                                 
                                             request.user.username), serilizer='json')

	return HttpResponseRedirect('/')







