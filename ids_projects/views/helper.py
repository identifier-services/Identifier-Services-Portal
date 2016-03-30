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
    """Collapses key-value pairs from nested 'value' field"""
    try:
        d = x['value']
    except Exception as e:
        logger.exception('{}'.format(e.message))

    try:
        d['uuid'] = x['uuid']
    except Exception as e:
        logger.exception('{}'.format(e.message))

    try:
        d['associationIds'] = x['associationIds']
    except Exception as e:
        logger.exception('{}'.format(e.message))

    try:
        d['name'] = x['name']
    except Exception as e:
        logger.exception('{}'.format(e.message))

    def make_short(s):
        if len(s) > 18:
            return s[:18] + "..."
        else:
            return s

    keys = d.keys()
    if 'title' in keys:
        d['short'] = make_short(d['title'])
    elif 'taxon_name' in keys:
        d['short'] = make_short(d['taxon_name'] + ' ' + d['specimen_id'])
    elif 'process_type' in keys:
        d['short'] = make_short(d['process_type'])

    return d
