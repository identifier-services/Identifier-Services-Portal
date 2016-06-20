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

    def save_base_metadata(self):
        """Reusable method for saving a base metadata object"""

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

        return base_meta

    def test_save_base_metadata(self):
        """Test saving a base metadata object"""

        self.save_base_metadata()

        # cleanup

        self.delete_base_metadata()

    def test_list_base_metadata(self):
        """Test listing metadata objects"""

        # start out by creating some metadata

        self.save_base_metadata()

        name = 'idsvc-test-meta'
        meta = { 'name': name }

        # then list metadata with name = 'idsvc-test-meta'

        base_meta = BaseMetadata(api_client=IDS_SYS_CLEINT, meta=meta)
        response = base_meta.list()

        # we should have at least one in the list, since we just created one

        self.assertTrue(len(response)>0)

        # cleanup

        self.delete_base_metadata()

    def test_load_from_agave(self):
        """Create a new BaseMetadata object and compare it to one from our list"""

        # create some metadata

        base_meta_object_a = self.save_base_metadata()

        # load the same metadata object again from agave

        base_meta_object_b = BaseMetadata(api_client=IDS_SYS_CLEINT, uuid=base_meta_object_a.uuid)
        base_meta_object_b.load_from_agave()

        # compare, make sure we're looking at the same thing (omitting
        # '_links', because listMetadata and getMetadata return a different
        # set of links.

        a = [(k,v) for k, v, in base_meta_object_a.__dict__.items() if k != '_links']
        b = [(k,v) for k, v, in base_meta_object_a.__dict__.items() if k != '_links']

        self.assertEqual(a, b)

        # cleanup

        self.delete_base_metadata()

    def test_edit_base_metadata(self):
        """Test editing a base metadata object"""

        # start out by creating some metadata

        base_meta_object_a = self.save_base_metadata()

        # load the same metadata object again from agave

        base_meta_object_b = BaseMetadata(api_client=IDS_SYS_CLEINT, uuid=base_meta_object_a.uuid)
        base_meta_object_b.load_from_agave()

        # compare, make sure we're looking at the same thing (omitting
        # '_links', because listMetadata and getMetadata return a different
        # set of links)

        a = [(k,v) for k, v, in base_meta_object_a.__dict__.items() if k != '_links']
        b = [(k,v) for k, v, in base_meta_object_a.__dict__.items() if k != '_links']

        self.assertEqual(a, b)

        # now let's edit, first add some information

        base_meta_object_a.body.update({'fruit':'apple'})

        # then save

        result = base_meta_object_a.save()

        # check to make sure we get the newly saved metadata objects in the result

        self.assertIn('uuid', result)

        # now check to make sure that a != b

        a = [(k,v) for k, v, in base_meta_object_a.__dict__.items() if k != '_links']

        self.assertNotEqual(a, b)

        # load again from agave just to be sure

        base_meta_object_a = BaseMetadata(api_client=IDS_SYS_CLEINT, uuid=base_meta_object_a.uuid)
        base_meta_object_a.load_from_agave()

        a = [(k,v) for k, v, in base_meta_object_a.__dict__.items() if k != '_links']

        self.assertNotEqual(a, b)

        # cleanup

        self.delete_base_metadata()

    def delete_base_metadata(self):
        """Delete all metadata with name = 'idsvc-test-meta'"""

        # get a list of metadata objects with name = 'idsvc-test-meta'

        name = 'idsvc-test-meta'
        meta = { 'name': name }

        base_meta = BaseMetadata(api_client=IDS_SYS_CLEINT, meta=meta)
        response = base_meta.list()

        # we will delete any and all metadata with name = 'idsvc-test-meta'

        for mo in response:
            mo.delete()

        # check delete, list metadata with name = 'idsvc-test-meta'

        base_meta = BaseMetadata(api_client=IDS_SYS_CLEINT, meta=meta)
        response = base_meta.list()

        self.assertEqual(len(response), 0)

    def test_delete_base_metadata(self):
        """Test deleting a base metadata object"""

        # start out by creating some metadata

        self.save_base_metadata()

        # delete all metadata with name = 'idsvc-test-meta'

        self.delete_base_metadata()

    def create_metadata_family(self):
        grandpa = self.save_base_metadata()

        pa = self.save_base_metadata()
        pa.associationIds.extend([grandpa.uuid]+[grandpa.associationIds])
        pa.save()

        sis = self.save_base_metadata()
        sis.associationIds.extend([pa.uuid]+[pa.associationIds])
        sis.save()

        brother = self.save_base_metadata()
        brother.associationIds.extend([pa.uuid]+[pa.associationIds])
        brother.save()

        cousin = self.save_base_metadata()
        cousin.associationIds.extend([grandpa.uuid]+[grandpa.associationIds])
        cousin.save()

        self.assertIn(grandpa.uuid, pa.associationIds)
        self.assertIn(grandpa.uuid, sis.associationIds)
        self.assertIn(grandpa.uuid, brother.associationIds)
        self.assertIn(grandpa.uuid, cousin.associationIds)

        self.assertIn(pa.uuid, sis.associationIds)
        self.assertIn(pa.uuid, brother.associationIds)

    def test_upstream_associated_metadata(self):
        """Test to see that model returns parent, grandparent objects"""

        # create some associated metadata

        self.create_metadata_family()

    def test_downstream_associated_metadata(self):
        """Test to see that model returns child objects"""

        # create some associated metadata

        self.create_metadata_family()
