from .base_agave_object import BaseAgaveObject
from .metadata_relationship_mixin import MetadataRelationshipMixin
from ids.utils import get_portal_api_client
import json
import datetime
import logging

logger = logging.getLogger(__name__)


class BaseMetadata(BaseAgaveObject, MetadataRelationshipMixin):
    """Base class for IDS Metadata (Project, Specimen, Process, Data)"""
    name = "idsvc.basemetadata"

    @classmethod
    def get_class_by_name(cls, name):
        """ """
        module_name = name.replace('idsvc.', '')
        class_name = module_name.title()

        if name not in locals():
            module = __import__(module_name, globals(), locals(), [class_name], -1)
            return getattr(module, class_name)
        else:
            return locals()[class_name]

    def __init__(self, *args, **kwargs):
        """Required Parameter:
            api_client      # AgavePy client
        Optional Parameters:
            uuid            # unique identifier for existing metadata object
            value            # information held in metadata 'value' field
            meta            # json or dictionary, values may include:
                            #   uuid, owner, schemaId, internalUsername,
                            #   associationIds, lastUpdated, name, value,
                            #   created, _links
            fields          # form fields for the object
        Explicit parameters take precedence over values found in the meta dictionary
        """
        super(BaseMetadata, self).__init__(*args, **kwargs)

        # create these instance variables for later
        self.uuid = None
        self.value = {}
        self.owner = None
        self.schemaId = None
        self.internalUsername = None
        self.associationIds = []
        self._links = []
        self._my_associations = None
        self._associations_to_me = None
        self._fields = None
        self._relationships = None
        self._related_objects = None

        # get optional arguments
        meta = kwargs.get('meta')
        value = kwargs.get('value')
        uuid = kwargs.get('uuid')
        fields = kwargs.get('fields')

        # set fields that are displayed in forms and detail view
        if fields is not None:
            self.set_fields(fields)

        # if uuid is provided explicitly and meta is not, load object from
        # agave and return
        if meta is None:
            meta = { 'uuid': None, 'value': {} }
            if uuid is not None:
                self.uuid = uuid
                self.load_from_agave()
                return

        # convert 'meta' to dictionary if necessary
        if type(meta) is str:
            meta = json.loads(meta)

        # convert 'value' to dictionary if necessary
        if type(value) is str:
            value = json.loads(value)

        # explicit constructor parameters take precedence over values found in
        # meta dictionary, so overwrite 'uuid' in meta if 'uuid' found in kwargs
        if uuid is not None:
            meta.update({ 'uuid': uuid })

        # explicit constructor parameters take precedence over values found in
        # meta dictionary, so overwrite 'value' in meta if 'value' found in kwargs
        if value is not None:
            meta.update({ 'value': value })

        # set instance variables
        self.load_from_meta(meta)

    def add_association_to(self, related_object):
        """
        Add the related object to this instance's my_associations list, and
        add the related object's uuid to this instance's associationIds list.
        Must save this instance to persist this association in Agave.
        """

        # check for uuid

        if 'uuid' not in dir(related_object) or related_object.uuid is None:
            exception_msg = "Related object must have a UUID to add "\
                            "association to this instance."
            raise Exception(exception_msg)

        # create a list of associated objects, include the related object
        # all all objects to which the related object is associated

        associated_objects = [related_object] + related_object.my_associations

        for associated_object in associated_objects:

            # skip if the object is already in the appropriate lists

            my_associations = self.my_associations
            associationIds  = self.associationIds

            if associated_object in my_associations \
                and associated_object.uuid in associationIds:
                continue # skip, go on to next association

            # add object if not already in the list

            if associated_object not in my_associations:
                self._my_associations.append(associated_object)

            # add object's uuid if not already in the list

            if associated_object.uuid not in associationIds:
                self.associationIds.append(associated_object.uuid)

            # call the object's add_association_from method, which will
            # add this instance only if it is not present the realted object's
            # associations_to_me list

            associated_object.add_association_from(self)

    def add_association_from(self, related_object):
        """
        Add this instance's UUID to a remote metadata object's associationIds list
        """

        # return if the object is already in the list

        if related_object in self.associations_to_me:
            return # already in the list

        # check for uuid

        if self.uuid is None:
            exception_msg = "This instance must have a UUID to add "\
                            "association from a related object."
            raise Exception(exception_msg)

        # add the related object if not already in the associations list

        self._associations_to_me.append(related_object)

        # call the object's add_association_to method, which will add this instance
        # only if it is not present the realted object's my_associations list

        related_object.add_association_to(self)

    @property
    def my_associations(self):
        """Retrieves all metadata objects corresponding to this instance's associationIds"""

        if self._my_associations is None:

            self._my_associations = []

            query = { 'uuid': { '$in': self.associationIds } }
            results = self._api_client.meta.listMetadata(q=json.dumps(query))

            for assoc_meta in results:

                assoc_object = self.get_class_by_name(assoc_meta.name)\
                                (meta=assoc_meta, api_client=self._api_client)

                self._my_associations.append(assoc_object)

        return self._my_associations

    @property
    def associations_to_me(self):
        """Retrieves all metadata objects that have this instance's UUID in their associationIds"""

        if self._associations_to_me is None:

            self._associations_to_me = []

            query = { 'associationIds': self.uuid }
            results = self._api_client.meta.listMetadata(q=json.dumps(query))

            for assoc_meta in results:

                assoc_object = self.get_class_by_name(assoc_meta.name)\
                                (meta=assoc_meta, api_client=self._api_client)

                self._associations_to_me.append(assoc_object)

        return self._associations_to_me

    def load_from_meta(self, meta):
        """Set instance variables from dictionary or json"""
        if type(meta) is str:
            meta = json.loads(meta)

        self.uuid = meta.get('uuid', None)
        self.value = meta.get('value', None)
        self.owner = meta.get('owner', None)
        self.schemaId = meta.get('schemaId', None)
        self.internalUsername = meta.get('internalUsername', None)
        self.associationIds = meta.get('associationIds', [])
        self._links = meta.get('_links', [])

        # TODO: instance variable for name is mixed up with list being an
        # instance method, make list a class method, pass in api_client
        if meta.get('name', None):
            self.name = meta.get('name', None)

        lastUpdated = meta.get('lastUpdated', None)
        if type(lastUpdated) is datetime.datetime:
            lastUpdated = lastUpdated.isoformat()
        self.lastUpdated = lastUpdated

        created = meta.get('created', None)
        if type(created) is datetime.datetime:
            created = created.isoformat()
        self.created = created

    def load_from_agave(self):
        """Load metadata from tenant, if UUID is not None"""
        meta = self._api_client.meta.getMetadata(uuid=self.uuid)

        created = meta.get('created').isoformat()
        lastUpdated = meta.get('lastUpdated').isoformat()

        # isoformat always same length, remove zeros in microsecond
        meta['created'] = created[:23] + created[26:]
        meta['lastUpdated'] = lastUpdated[:23] + lastUpdated[26:]

        self.load_from_meta(meta)

    def set_fields(self, fields):
        """ """
        field_dict = {}
        for field in fields:
            key = field.get('id').replace(' ', '_')
            label = field.get('label')
            field_class = field.get('field_class')
            widget = field.get('widget')
            required = field.get('required')
            choices = field.get('choices')
            field_dict[key] = {
                'label': label,
                'field_class':field_class,
                'widget': widget,
                'required': required,
                'choices': choices,
            }
        self._fields = field_dict

    @property
    def fields(self):
        return self._fields

    @classmethod
    def list(cls, api_client):
        """List idsvc objects accessible to the client"""
        query = {'name': cls.name}
        results = api_client.meta.listMetadata(q=json.dumps(query))

        if results is not None:
            return [cls(meta=r, api_client=api_client) for r in results]

    def share(self, username=None, permission='READ_WRITE'):
        """
        Grant permissions on this metadata object to other users.  This metadata object
        must have a UUID.

        :param username:    The username of the api user whose permission is to be set.
                            (Default: portal's user account)
        :param permission:  ['READ' or 'WRITE' or 'READ_WRITE' or 'ALL' or 'NONE']:
                            The permission to set. (Default: READ_WRITE)
        :return: None
        """
        if self.uuid is None:
            raise Exception('Cannot grant permissions, objects does not have a UUID.')

        if not username:
            username = get_portal_api_client().profiles.get().username

        perm_result = self._api_client.meta.updateMetadataPermissions(
            uuid=self.uuid,
            body={
                'username': username,
                'permission': permission
            })

        return perm_result

    def save(self):
        """Add or update metadata object on tenant"""

        # if self.name == 'idsvc.data':
        #     import pdb
        #     pdb.set_trace()

        if self.uuid is None:
            response = self._api_client.meta.addMetadata(body=self.meta)
            self.load_from_meta(response)
            # TODO: get rid of share result, I just want to see what comes back.
            share_result = self.share()
            logger.debug('Sharing result: {}'.format(share_result))
        else:
            response = self._api_client.meta.updateMetadata(uuid=self.uuid, body=self.meta)
            self.load_from_meta(response)

    def delete(self):
        """Delete metadata object, and all metadata associated to this object"""
        if self.uuid is None:
            raise Exception('Cannot delete without UUID.')

        # delete all objects that have this object's uuid in their associationIds
        #TODO: remove this
        for item in self.associations_to_me:
            item.delete()

        logger.debug('deleting object: %s - %s' % (self.title, self.uuid))
        self._api_client.meta.deleteMetadata(uuid=self.uuid)
        self.uuid = None

    @property
    def title(self):
        return self.value.get('name')

    @property
    def meta(self):
        """Dictionary containing all relevant data and metadata. Fields may include:

            uuid, owner, schemaId, internalUsername, associationIds, lastUpdated,
            name, created, value (may contain an embedded dictionary), _links
        """
        value = self.value

        if self.uuid is not None:
            relationships = self.relationships
        else:
            relationships = []

        for relationship in relationships:
            if '@id' not in relationship.keys():
                logger.warning('This is not the right type of relationship! %s' % relationship)
                raise Exception('Invalid dictionary contained in list of relationship')

        # TODO: implement namespaces throughout the application
        # if type(value) is dict:
        #     value.update({ '@dc:name': self.title })
        #     value.update({ '_relationships': relationships})
        # elif value is None:
        #     value = { '@dc:name': self.title,
        #               '@dc:creator': self.me,
        #               '@ids:type': self.name.split('.')[1:],
        #               '_relationships': relationships
        #               }

        # implementing namespaces will take some work, so I'm leaving them out for the moment
        if type(value) is dict:
            value.update({ 'name': self.title })
            value.update({ '_relationships': relationships})
        elif value is None:
            value = { 'name': self.title,
                      'creator': self.me,
                      'type': self.name.split('.')[1:],
                      '_relationships': relationships
                      }

        return { 'uuid': self.uuid,
                 'owner': self.owner,
                 'schemaId': self.schemaId,
                 'internalUsername': self.internalUsername,
                 'associationIds': self.associationIds,
                 'lastUpdated': self.lastUpdated,
                 'name': self.name,
                 'created': self.created,
                 'value': value,
                 '_links': self._links }

    def to_json(self):
        """The meta property, formatted as json string"""
        return json.dumps(self.meta)
