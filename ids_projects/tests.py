from django.test import TestCase
from agavepy.agave import Agave
from more_efficient_models import (BaseAgaveObject, BaseMetadata, Project,
                                   Specimen, Process, Data)
import os

# import subprocess
# base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# test_path = os.path.join(base_dir,'test.env')
# subprocess.call(['/bin/bash',test_path])

# instantiating these clients outside of the test suite setup method might be
# frowned upon, but I only want to create the clients once. it's time consuming.


AGAVE_TENANT_BASEURL = os.environ.get('AGAVE_TENANT_BASEURL')
IDS_SYS_SUPER_TOKEN = os.environ.get('IDS_SYS_SUPER_TOKEN')
TEST_USER1_SUPER_TOKEN = os.environ.get('TEST_USER1_SUPER_TOKEN')
TEST_USER2_SUPER_TOKEN = os.environ.get('TEST_USER2_SUPER_TOKEN')

IDS_SYS_CLEINT = Agave(api_server=AGAVE_TENANT_BASEURL, token=IDS_SYS_SUPER_TOKEN)
TEST_USER1_CLIENT = Agave(api_server=AGAVE_TENANT_BASEURL, token=TEST_USER1_SUPER_TOKEN)
TEST_USER2_CLIENT = Agave(api_server=AGAVE_TENANT_BASEURL, token=TEST_USER2_SUPER_TOKEN)


class BaseClientTests(object):
    """Test class is inteded to be inherited"""

    # make sure we got the env variables

    def test_environ_tenant_baseurl(self):
        """Did we get the baseurl env variable?"""
        self.assertIsNotNone(AGAVE_TENANT_BASEURL)

    def test_environ_sys_token(self):
        """Did we get the ids sys super token env variable?"""
        self.assertIsNotNone(IDS_SYS_SUPER_TOKEN)

    def test_environ_testuser1_token(self):
        """Did we get the test user 1 env variable?"""
        self.assertIsNotNone(TEST_USER1_SUPER_TOKEN)

    def test_environ_testuser2_token(self):
        """Did we get the test user 2 env variable?"""
        self.assertIsNotNone(TEST_USER2_SUPER_TOKEN)

    # make sure we can use out clients

    def test_sys_client(self):
        """Test ids sys client, should return dict with username for profiles.listByUsername"""
        self.assertIsNotNone(IDS_SYS_CLEINT.profiles.listByUsername(username='me'))

    def test_testuser1_client(self):
        """Test test user 1 client, should return dict with username for profiles.listByUsername"""
        self.assertIsNotNone(TEST_USER1_CLIENT.profiles.listByUsername(username='me'))

    def test_testuser2_client(self):
        """Test test user 2 client, should return dict with username for profiles.listByUsername"""
        self.assertIsNotNone(TEST_USER2_CLIENT.profiles.listByUsername(username='me'))


class BaseMetadataTests(TestCase, BaseClientTests):
    """Tests for BaseAgaveObject and BaseMetadata in IDS models"""

    def test_base_agave_object(self):
        """Test instantiation of base object"""
        base_object = BaseAgaveObject(api_client=IDS_SYS_CLEINT)
        self.assertIsNotNone(base_object)
        self.assertEqual(base_object._api_client, IDS_SYS_CLEINT)

    def test_base_metadata(self):
        """Test instantiation of base metadata object"""
        base_meta = BaseMetadata(api_client=IDS_SYS_CLEINT)
        self.assertIsNotNone(base_meta)
        self.assertEqual(base_meta._api_client, IDS_SYS_CLEINT)

    def test_uuid_base_metadata_param(self):
        """Test uuid parameter to base metadata constructor"""
        uuid = 'ABC'
        base_meta = BaseMetadata(api_client=IDS_SYS_CLEINT, uuid=uuid)
        self.assertEqual(base_meta.uuid, uuid)

    def test_body_base_metadata_param(self):
        """Test body parameter to base metadata constructor"""
        body = { 'color': 'blue' }
        base_meta = BaseMetadata(api_client=IDS_SYS_CLEINT, body=body)
        self.assertEqual(base_meta.body, body)

    def test_meta_base_metadata_param(self):
        """Test meta parameter to base metadata constructor"""
        name = 'idsvc-test-meta'
        meta = { 'name': name }
        base_meta = BaseMetadata(api_client=IDS_SYS_CLEINT, meta=meta)
        # base_meta.meta will return null values that we did not specifiy
        # so we need to test if meta is a subset of base_meta.meta
        self.assertTrue(all(item in base_meta.meta.items() for item in meta.items()))

    def test_name_attribute_in_base_metadata(self):
        """Test name attribute in base metadata object"""
        name = 'idsvc-test-meta'
        meta = { 'name': name }
        base_meta = BaseMetadata(api_client=IDS_SYS_CLEINT, meta=meta)
        self.assertEqual(base_meta.name, meta['name'])

    def test_all_attributes_in_base_metadata(self):
        """Test name attribute in base metadata object"""

        name = 'idsvc-test-meta'
        uuid = 'ABC'
        body = { 'color': 'blue' }
        owner = 'bob'
        schemaId = None
        internalUsername = None
        associationIds = ['CDE', 'EFG']
        lastUpdated = '2016-06-15T17:09:06.137-05:00'
        name = 'idsvc-test-meta'
        created = '2016-06-15T17:09:06.137-05:00'
        _links =  ''

        meta = {
            'name': name,
            'uuid': uuid,
            'value': body,
            'owner': owner,
            'schemaId': schemaId,
            'internalUsername': internalUsername,
            'associationIds': associationIds,
            'lastUpdated': lastUpdated,
            'name': name,
            'created': created,
            '_links': _links
         }

        base_meta = BaseMetadata(api_client=IDS_SYS_CLEINT, meta=meta)
        self.assertDictEqual(base_meta.meta, meta)

    def test_save_base_metadata(self):
        """Test saving a base metadata object"""

        name = 'idsvc-test-meta'
        body = { 'color': 'blue' }
        name = 'idsvc-test-meta'

        meta = { 'name': name,
                 'value': body,
                 'name': name }

        base_meta = BaseMetadata(api_client=IDS_SYS_CLEINT, meta=meta)
        response = base_meta.save()
        self.assertIn('uuid', response)
        self.assertIsNotNone(base_meta.uuid)

        self.assertTrue(all(item in base_meta.meta.items() for item in meta.items()))

    # def test_save_delete_meta(self):
    #     """Test save and delete, I don't know the best way to do this..."""
    #     self.assertIsEqual(1,2)
