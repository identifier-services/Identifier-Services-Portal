from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from agavepy.agave import Agave, AgaveException
import json, logging
from forms import ProjectForm


logger = logging.getLogger(__name__)

def _client(request):
    token = request.session.get(getattr(settings, 'AGAVE_TOKEN_SESSION_ID'))
    access_token = token.get('access_token', None)
    url = getattr(settings, 'AGAVE_TENANT_BASEURL')
    return Agave(api_server = url, token = access_token)

def index(request):
    token = request.session.get(getattr(settings, 'AGAVE_TOKEN_SESSION_ID'))
    access_token = token.get('access_token', None)
    url = getattr(settings, 'AGAVE_TENANT_BASEURL')

    try:
        a = Agave(api_server = url, token = access_token)
        query = {'name':'idsvc.project'}
        l = a.meta.listMetadata(q=json.dumps(query))
    except AgaveException as e:
        return HttpResponse('{{"error": "{0}" }}'.format(json.dumps(e.message)),
            status = 500, content_type='application/json')
    except Exception as e:
        return HttpResponse('{{"error": "{0}" }}'.format(json.dumps(e.message)),
            status = 500, content_type='application/json')

    return render(request, 'ids_projects/index.html', {'data':l})

@login_required
def create(request):
    if request.method == 'POST':

        form = ProjectForm(request.POST)

        if form.is_valid():

            title = form.cleaned_data['title']
            inv_type = form.cleaned_data['investigation_type']
            desc = form.cleaned_data['description']

            body = {
                "name":"idsvc.project",
                "value": {
                    "title":title,
                    "investigation_type":inv_type,
                    "description":desc,
                }
            }
            a = _client(request)
            try:
                response = a.meta.addMetadata(body=body)
            except Exception as e:
                logger.debug('no sir: %s' % e)

            return HttpResponseRedirect('/projects/')
    # else:
    context = {
        'form': ProjectForm()
    }

    return render(request, 'ids_projects/create.html', context)

def detail(request, uuid):
    a = _client(request)
    query = {'uuid':uuid}
    project = a.meta.listMetadata(q=json.dumps(query))[0]

    specimens_query = {'name':'idsvc.specimen','associationIds':'{}'.format(uuid)}
    specimens = a.meta.listMetadata(q=json.dumps(specimens_query))

    associatedIds = [uuid] # project id

    for specimen in specimens:
        data_query = {'name':'idsvc.data','associationIds':specimen.uuid}
        data = a.meta.listMetadata(q=json.dumps(data_query))
        specimen.data = data
        #associatedIds.append(specimen.uuid)

    #TODO: work on $or mongo query
    datasets_query = {'name':'idsvc.dataset','associationIds':'{}'.format(
                        associatedIds[0])}

    datasets = a.meta.listMetadata(q=json.dumps(datasets_query))

    for dataset in datasets:
        data_query = {'name':'idsvc.data','associationIds':dataset.uuid}
        data = a.meta.listMetadata(q=json.dumps(data_query))
        dataset.data = data

    return render(request,
        'ids_projects/detail.html',
        {
            'project':project,
            'specimens':specimens,
            'datasets':datasets,
        }
    )

@login_required
def delete(request, uuid):
    a = _client(request)
    a.meta.deleteMetadata(uuid=uuid)
    return HttpResponseRedirect('/projects/')
