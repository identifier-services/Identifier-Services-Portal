from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from agavepy.agave import Agave, AgaveException
import json, logging
from forms import ProjectForm, SystemForm


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
            else:
                print "response: {}".format(response)

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
        associatedIds.append(specimen.uuid)

    #TODO: work on $or mongo query
    datasets_query = {'name':'idsvc.dataset','associationIds':'{}'.format(
                        associatedIds[0])}

    datasets = a.meta.listMetadata(q=json.dumps(datasets_query))

    print " *** datasets: {} *** ".format(json.dumps(datasets))

    print " *** dataset query: {} *** ".format(json.dumps(datasets_query))

    files = [{'value':{'name':'data.txt'}},{'value':{'name':'data.txt'}}]

    return render(request,
        'ids_projects/detail.html',
        {
            'project':project,
            'specimens':specimens,
            'datasets':datasets,
            'files':files,
        }
    )

@login_required
def delete(request, uuid):
    a = _client(request)
    a.meta.deleteMetadata(uuid=uuid)
    return HttpResponseRedirect('/projects/')

@login_required
def dataset(request, uuid):
    if request.method == 'POST':
        form = SystemForm(request.POST)

        if form.is_valid():
            choice = form.cleaned_data['system']
            logger.debug(choice)
            return HttpResponseRedirect('/projects/')

    body = {
        "name":"idsvc.dataset",
        "associationIds": [uuid],
        "value": {
            "dataset_type:" : "process"
        }
    }
    a = _client(request)
    dataset = a.meta.addMetadata(body=body)

    query = {'uuid':uuid}
    project = a.meta.listMetadata(q=json.dumps(query))[0]

    systems = a.systems.list(type='STORAGE')
    system_choices = []
    for system in systems:
        choice_tuple = (system.name,system.name)
        system_choices.append(choice_tuple)

    return render(
        request,
        'ids_projects/dataset.html',
        {
            'project':project,
            'dataset':dataset,
            'systems':systems,
            'form':SystemForm(system_choices)
        }
    )

@login_required
def data(request, uuid):
    body = {
        "name":"idsvc.data",
        "associationIds": [uuid],
        "value": {}
    }
    a = _client(request)
    data = a.meta.addMetadata(body=body)

    dataset_query = {'uuid':uuid}
    dataset = a.meta.listMetadata(q=json.dumps(dataset_query))[0]

    project_id = dataset.associationIds[0]

    project_query = {'name':'idsvc.project','uuid':project_id}
    project = a.meta.listMetadata(q=json.dumps(project_query))[0]

    system = a.systems.get(systemId='data.iplantcollaborative.org')

    query = {'uuid':uuid}
    files = a.files.list(systemId='data.iplantcollaborative.org',filePath='amagill')

    return render(
        request,
        'ids_projects/data.html',
        {
            'project':project,
            'data':data,
            'dataset':dataset,
            'system':system,
            'files':files
        }
    )
