from django.conf import settings
from agavepy.agave import Agave


def get_portal_api_client():
    return Agave(api_server=settings.AGAVE_TENANT_BASEURL,
                 token=settings.AGAVE_SUPER_TOKEN)
