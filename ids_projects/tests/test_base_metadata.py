from django.test import TestCase
from ..models import BaseAgaveObject, BaseMetadata
from test_client import TestClient


class BaseMetadataTests(TestCase, TestClient):
    """Tests for BaseAgaveObject and BaseMetadata in IDS models"""

    def test_base_agave_object(self):
        """Test instantiation of base object"""
        base_object = BaseAgaveObject(api_client=self.IDS_SYS_CLIENT)
        self.assertIsNotNone(base_object)
        self.assertEqual(base_object._api_client, self.IDS_SYS_CLIENT)

    def test_base_metadata(self):
        """Test instantiation of base metadata object"""
        base_meta = BaseMetadata(api_client=self.IDS_SYS_CLIENT)
        self.assertIsNotNone(base_meta)
        self.assertEqual(base_meta._api_client, self.IDS_SYS_CLIENT)

    # def test_uuid_base_metadata_param(self):
    #     """Test uuid parameter to base metadata constructor"""
    #     uuid = 'ABC'
    #     base_meta = BaseMetadata(api_client=self.IDS_SYS_CLIENT, uuid=uuid)
    #     self.assertEqual(base_meta.uuid, uuid)

    def test_value_base_metadata_param(self):
        """Test value parameter to base metadata constructor"""
        value = { 'color': 'blue' }
        base_meta = BaseMetadata(api_client=self.IDS_SYS_CLIENT, value=value)
        self.assertEqual(base_meta.value, value)

    def test_meta_base_metadata_param(self):
        """Test meta parameter to base metadata constructor"""
        name = 'idsvc.basemeta'
        meta = { 'name': name }
        base_meta = BaseMetadata(api_client=self.IDS_SYS_CLIENT, meta=meta)
        # base_meta.meta will return null values that we did not specifiy
        # so we need to test if meta is a subset of base_meta.meta
        self.assertTrue(all(item in base_meta.meta.items() for item in meta.items()))

    def test_name_attribute_in_base_metadata(self):
        """Test name attribute in base metadata object"""
        name = 'idsvc.basemeta'
        meta = { 'name': name }
        base_meta = BaseMetadata(api_client=self.IDS_SYS_CLIENT, meta=meta)
        self.assertEqual(base_meta.name, meta['name'])

    def test_all_attributes_in_base_metadata(self):
        """Test name attribute in base metadata object"""

        name = 'idsvc.basemeta'
        uuid = 'ABC'
        value = { 'color': 'blue' }
        owner = 'bob'
        schemaId = None
        internalUsername = None
        associationIds = ['CDE', 'EFG']
        lastUpdated = '2016-06-15T17:09:06.137-05:00'
        name = 'idsvc.basemeta'
        created = '2016-06-15T17:09:06.137-05:00'
        _links =  ''

        meta = {
            'name': name,
            'uuid': uuid,
            'value': value,
            'owner': owner,
            'schemaId': schemaId,
            'internalUsername': internalUsername,
            'associationIds': associationIds,
            'lastUpdated': lastUpdated,
            'name': name,
            'created': created,
            '_links': _links
         }

        base_meta = BaseMetadata(api_client=self.IDS_SYS_CLIENT, meta=meta)
        self.assertDictEqual(base_meta.meta, meta)

    def save_base_metadata(self):
        """Reusable method for saving a base metadata object"""
        value = { 'color': 'blue' }
        meta = { 'value': value }
        base_meta = BaseMetadata(api_client=self.IDS_SYS_CLIENT, meta=meta)
        base_meta.save()
        self.assertIsNotNone(base_meta.uuid)
        self.assertTrue(all([item in base_meta.meta.items() for item in meta.items()]))
        return base_meta

    def test_save_base_metadata(self):
        """Test saving a base metadata object"""

        self.save_base_metadata()

        # cleanup

        self.delete_base_metadata()

    def test_save_with_no_meta(self):
        """Test saving without providing metadata"""

        base_meta = BaseMetadata(api_client=self.IDS_SYS_CLIENT)

        base_meta.save()
        self.assertIsNotNone(base_meta.uuid)

        # cleanup

        self.delete_base_metadata()

    def test_save_with_value_no_meta(self):
        """Test saving with value but without 'meta'"""

        value = { 'color': 'blue' }

        base_meta = BaseMetadata(api_client=self.IDS_SYS_CLIENT, value=value)

        base_meta.save()
        self.assertIsNotNone(base_meta.uuid)

        self.assertTrue(all(item in base_meta.value.items() for item in value.items()))

        # cleanup

        self.delete_base_metadata()

    def test_list_base_metadata(self):
        """Test listing metadata objects"""

        # start out by creating some metadata

        self.save_base_metadata()

        # then list metadata with name = 'idsvc.basemeta'

        response = BaseMetadata.list(api_client=self.IDS_SYS_CLIENT)

        # we should have at least one in the list, since we just created one

        self.assertTrue(len(response)>0)

        # cleanup

        self.delete_base_metadata()

    def test_load_from_agave(self):
        """Create a new BaseMetadata object and compare it to one from our list"""

        # create some metadata

        base_meta_object_a = self.save_base_metadata()

        # load the same metadata object again from agave

        base_meta_object_b = BaseMetadata(api_client=self.IDS_SYS_CLIENT, uuid=base_meta_object_a.uuid)
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

        base_meta_object_b = BaseMetadata(api_client=self.IDS_SYS_CLIENT, uuid=base_meta_object_a.uuid)
        base_meta_object_b.load_from_agave()

        # compare, make sure we're looking at the same thing (omitting
        # '_links', because listMetadata and getMetadata return a different
        # set of links)

        a = [(k,v) for k, v, in base_meta_object_a.__dict__.items() if k != '_links']
        b = [(k,v) for k, v, in base_meta_object_a.__dict__.items() if k != '_links']

        self.assertEqual(a, b)

        # now let's edit, first add some information

        base_meta_object_a.value.update({'fruit':'apple'})

        # then save

        base_meta_object_a.save()

        # check to make sure we have a uuid, means save was succeeded

        self.assertIsNotNone(base_meta_object_a.uuid)

        # now check to make sure that a != b

        a = [(k,v) for k, v, in base_meta_object_a.__dict__.items() if k != '_links']

        self.assertNotEqual(a, b)

        # load again from agave just to be sure

        base_meta_object_a = BaseMetadata(api_client=self.IDS_SYS_CLIENT, uuid=base_meta_object_a.uuid)
        base_meta_object_a.load_from_agave()

        a = [(k,v) for k, v, in base_meta_object_a.__dict__.items() if k != '_links']

        self.assertNotEqual(a, b)

        # cleanup

        self.delete_base_metadata()

    def delete_base_metadata(self):
        """Delete all metadata with name = 'idsvc.basemeta'"""

        # get a list of basemetadata objects

        response = BaseMetadata.list(self.IDS_SYS_CLIENT)

        # we will delete any and all metadata with name = 'idsvc.basemeta'

        for mo in response:
            mo.delete()

        # check delete, list metadata with name = 'idsvc.basemeta'

        response = BaseMetadata.list(self.IDS_SYS_CLIENT)

        self.assertEqual(len(response), 0)

    def test_delete_base_metadata(self):
        """Test deleting a base metadata object"""

        # start out by creating some metadata

        self.save_base_metadata()

        # delete all metadata with name = 'idsvc.basemeta'

        self.delete_base_metadata()

    def printy(self, oj, a, b, c, d, e):
        print "\n  {:<15}{:<15}".format('assoc','remote assoc')
        if a is not None: print "A {:<15}{:<15}".format([oj[x] for x in a.associationIds], [oj[x.uuid] for x in a.associations_to_me])
        if b is not None: print "B {:<15}{:<15}".format([oj[x] for x in b.associationIds], [oj[x.uuid] for x in b.associations_to_me])
        if c is not None: print "C {:<15}{:<15}".format([oj[x] for x in c.associationIds], [oj[x.uuid] for x in c.associations_to_me])
        if d is not None: print "D {:<15}{:<15}".format([oj[x] for x in d.associationIds], [oj[x.uuid] for x in d.associations_to_me])
        if e is not None: print "E {:<15}{:<15}".format([oj[x] for x in e.associationIds], [oj[x.uuid] for x in e.associations_to_me])
        print

    def test_associations(self):
        """Create a few metadata objects with associations, and test to see
        that model returns appropriate associations between objects"""

        oj = {}

        if self.DEBUG:
            print "Create A"

        # create a
        a = self.save_base_metadata()

        oj[a.uuid] = 'A'

        if self.DEBUG:
            print "Create B, point B to A"

        # create b, point b to a
        b = self.save_base_metadata()

        oj[b.uuid] = 'B'

        b.add_association_to(a)

        # save a, b
        b.save()
        a.save()

        if self.DEBUG:
            self.printy(oj, a, b, None, None, None)

        # test b pointing to a
        self.assertIn(a, b.my_associations)
        # test to see if a is aware of association from b
        # self.assertIn(b, a.associations_to_me)

        if self.DEBUG:
            print "Create C, point C to B"

        # create c, point c to b
        c = self.save_base_metadata()

        oj[c.uuid] = 'C'

        c.add_association_to(b)

        # a.save()

        # save b, c
        c.save()
        b.save()

        if self.DEBUG:
            self.printy(oj, a, b, c, None, None)

        # test c pointing to a
        self.assertIn(a, c.my_associations)
        # test c aware of association from a
        self.assertIn(c, a.associations_to_me)

        # test c pointing to b
        self.assertIn(b, c.my_associations)
        # test b aware of association from c
        self.assertIn(c, b.associations_to_me)

        if self.DEBUG:
            print "create D, point to B"

        # create d, point to b
        d = self.save_base_metadata()

        oj[d.uuid] = 'D'

        d.add_association_to(b)

        # a.save()

        # save d, b
        d.save()
        b.save()

        if self.DEBUG:
            self.printy(oj, a, b, c, d, None)

        # test d pointing to a
        self.assertIn(a, d.my_associations)
        # test a aware of assoication from d
        self.assertIn(d, a.associations_to_me)

        # test d pointing to b
        self.assertIn(b, d.my_associations)
        # test b aware of association from d
        self.assertIn(d, b.associations_to_me)

        if self.DEBUG:
            print "Create E, point to A"

        # create e, point to a
        e = self.save_base_metadata()

        oj[e.uuid] = 'E'

        e.add_association_to(a)

        # save e, a
        e.save()
        a.save()

        if self.DEBUG:
            self.printy(oj, a, b, c, d, e)

        # test e pointing to a
        self.assertIn(a, e.my_associations)
        # test a aware of association from e
        self.assertIn(b, a.associations_to_me)
