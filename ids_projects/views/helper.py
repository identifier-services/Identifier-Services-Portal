import logging
from django.conf import settings
from agavepy.agave import Agave, AgaveException


logger = logging.getLogger(__name__)


def client(request):
    token = request.session.get(getattr(settings, 'AGAVE_TOKEN_SESSION_ID'))
    access_token = token.get('access_token', None)
    logger.debug("access token: {}".format(access_token))
    url = getattr(settings, 'AGAVE_TENANT_BASEURL')
    return Agave(api_server = url, token = access_token)


def collapse_meta(x):
    d = x['value']
    d['uuid'] = x['uuid']
    d['associationIds'] = x['associationIds']
    d['name'] = x['name']
    return d
