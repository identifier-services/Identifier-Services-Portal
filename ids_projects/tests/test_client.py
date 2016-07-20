from agavepy.agave import Agave
import os


class TestClient(object):
    AGAVE_TENANT_BASEURL = os.environ.get('AGAVE_TENANT_BASEURL')
    IDS_SYS_SUPER_TOKEN = os.environ.get('IDS_SYS_SUPER_TOKEN')
    TEST_USER1_SUPER_TOKEN = os.environ.get('TEST_USER1_SUPER_TOKEN')
    TEST_USER2_SUPER_TOKEN = os.environ.get('TEST_USER2_SUPER_TOKEN')

    IDS_SYS_CLIENT = Agave(api_server=AGAVE_TENANT_BASEURL,
                           token=IDS_SYS_SUPER_TOKEN)

    TEST_USER1_CLIENT = Agave(api_server=AGAVE_TENANT_BASEURL,
                              token=TEST_USER1_SUPER_TOKEN)

    TEST_USER2_CLIENT = Agave(api_server=AGAVE_TENANT_BASEURL,
                              token=TEST_USER2_SUPER_TOKEN)

    DEBUG = False
