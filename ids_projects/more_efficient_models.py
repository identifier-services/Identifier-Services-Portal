import json, datetime, logging

logger = logging.getLogger(__name__)


class BaseAgaveObject(object):
    """Anything that we want in all our Agave objects, contains only the api
    client at the moment."""
    def __init__(self, api_client, *args, **kwargs):
        # TODO: if type(api_client) is not agavepy.agave.Agave: raise Exception()
        self._api_client = api_client


class BaseMetadata(BaseAgaveObject):
    """Base class for IDS Metadata (Project, Specimen, Process, Data)"""
    name = "idsvc.basemetadata"

    def __init__(self, *args, **kwargs):
        """Required Parameter:
            api_client      # AgavePy client
        Optional Parameters:
            uuid            # unique identifier for existing metadata object
            body            # information held in metadata 'value' field
            meta            # json or dictionary, values may include:
                            #   uuid, owner, schemaId, internalUsername,
                            #   associationIds, lastUpdated, name, value,
                            #   created, _links
        Explicit parameters take precedence over values found in the meta dictionary
        """
        super(BaseMetadata, self).__init__(*args, **kwargs)

        # create these instance variables for later

        self.uuid = None
        self.body = {}
        self.owner = None
        self.schemaId = None
        self.internalUsername = None
        self.associationIds = None
        # self.name = None
        self._links = None
        self._my_associations = None
        self._associations_to_me = None

        # get meta if passed to constructor, convert to dict if necessary

        meta = kwargs.get('meta', {})
        if type(meta) is str:
            meta = json.loads(meta)
        self.load_from_meta(meta)

        # explicit constructor parameters take precedence over values found in
        # meta dictionary (namely 'uuid', and 'value' aka 'body')

        body = kwargs.get('body', meta.get('value', {}))
        if type(body) is str:
            body = json.loads(body)
        self.body = body
        self.uuid = kwargs.get('uuid', meta.get('uuid', None))

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

            if associated_object in self.my_associations \
                and associated_object.uuid in self.associationIds:
                continue

            # add object if not already in the list

            if associated_object not in self.my_associations:
                self.my_associations.append(associated_object)

            # add object's uuid if not already in the list

            if associated_object.uuid not in self.associationIds:
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
            return

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
            query = { 'uuid': { '$in': self.associationIds } }
            results = self._api_client.meta.listMetadata(q=json.dumps(query))
            self._my_associations = [self.make(meta=r, api_client=self._api_client) for r in results]

        return self._my_associations

    @property
    def associations_to_me(self):
        """Retrieves all metadata objects that have this instance's UUID in their associationIds"""

        if self._associations_to_me is None:
            query = { 'associationIds': self.uuid }
            results = self._api_client.meta.listMetadata(q=json.dumps(query))
            self._associations_to_me = [self.make(meta=r, api_client=self._api_client) for r in results]

        return self._associations_to_me

    def load_from_meta(self, meta):
        """Set instance variables from dictionary or json"""
        if type(meta) is str:
            meta = json.loads(meta)

        self.uuid = meta.get('uuid', None)
        if meta.get('value', None):
            self.body = meta.get('value', None)
        self.owner = meta.get('owner', None)
        self.schemaId = meta.get('schemaId', None)
        self.internalUsername = meta.get('internalUsername', None)
        self.associationIds = meta.get('associationIds', None)
        if meta.get('name', None):
            self.name = meta.get('name', None)
        self._links = meta.get('_links', None)

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

    @classmethod
    def make(cls, meta, api_client, *args, **kwargs):
        return cls(meta=meta, api_client=api_client, *args, **kwargs)

    def list(self):
        query = {'name': self.name}
        results = self._api_client.meta.listMetadata(q=json.dumps(query))

        if results is not None:
            return [self.make(meta=r, api_client=self._api_client) for r in results]

    def save(self):
        """Add or update metadata object on tenant"""

        if self.uuid is None:
            response = self._api_client.meta.addMetadata(body=self.meta)
        else:
            response = self._api_client.meta.updateMetadata(uuid=self.uuid, body=self.meta)
        self.load_from_meta(response)

        return response

    def delete(self):
        """Delete metadata object, and all metadata associated to this object"""
        if self.uuid is None:
            raise Exception('Cannot delete without UUID.')

        # delete all objects that have this object's uuid in their associationIds
        for item in self.associations_to_me:
            item.delete()

        response = self._api_client.meta.deleteMetadata(uuid=self.uuid)
        self.uuid = None
        return response

    @property
    def meta(self):
        """Dictionary containing all relevant data and metadata. Fields may include:

            uuid, owner, schemaId, internalUsername, associationIds, lastUpdated,
            name, created, value (may contain an embedded dictionary), _links
        """
        # TODO: I'm not sure if it makes sense to strip out null values
        return { 'uuid': self.uuid,
                 'owner': self.owner,
                 'schemaId': self.schemaId,
                 'internalUsername': self.internalUsername,
                 'associationIds': self.associationIds,
                 'lastUpdated': self.lastUpdated,
                 'name': self.name,
                 'created': self.created,
                 'value': self.body,
                 '_links': self._links }

    def to_json(self):
        """The meta property, formatted as json string"""
        return json.dumps(self.meta)


class Project(BaseMetadata):
    """ """
    name = 'idsvc.project'

    def __init__(self, *args, **kwargs):
        """ """
        super(Project, self).__init__(*args, **kwargs)

    @property
    def specimens(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.specimen']

    @property
    def processes(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.process']

    @property
    def data(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.data']


class Specimen(BaseMetadata):
    """ """
    name = 'idsvc.specimen'

    def __init__(self, *args, **kwargs):
        """ """
        super(Specimen, self).__init__(*args, **kwargs)

    @property
    def project(self):
        return [x for x in self.my_associations if x.name == 'idsvc.project']

    @property
    def process(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.process']

    @property
    def data(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.data']


class Process(BaseMetadata):
    """ """
    name = 'idsvc.process'

    def __init__(self, *args, **kwargs):
        """ """
        super(Process, self).__init__(*args, **kwargs)

    @property
    def project(self):
        return [x for x in self.my_associations if x.name == 'idsvc.project']

    @property
    def specimens(self):
        return [x for x in self.my_associations if x.name == 'idsvc.specimen']

    @property
    def data(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.data']

    @property
    def inputs(self):
        return [x for x in self.data if x.uuid in self.body['_inputs']]

    @property
    def outputs(self):
        return [x for x in self.data if x.uuid in self.body['_outputs']]

class Data(BaseMetadata):
    """ """
    name = 'idsvc.data'

    def __init__(self, *args, **kwargs):
        """ """
        super(Data, self).__init__(*args, **kwargs)

    @property
    def project(self):
        return [x for x in self.my_associations if x.name == 'idsvc.project']

    @property
    def specimens(self):
        return [x for x in self.my_associations if x.name == 'idsvc.specimen']

    @property
    def processes(self):
        return [x for x in self.my_associations if x.name == 'idsvc.process']

    def calculate_checksum(self):
        name = "checksum"
        app_id = "idsvc_checksum-0.1"
        archive = False

        if self.sra_id:
            parameters = { 'UUID': self.uuid, 'SRA': self.sra_id }
            body={'name': name, 'appId': app_id, 'parameters': parameters}
        else:
            agave_url = "agave://%s/%s" % (self.system_id, self.path)
            inputs = { 'AGAVE_URL': agave_url }
            parameters = { 'UUID': self.uuid }
            body={'name': name, 'appId': app_id, 'inputs': inputs, 'parameters': parameters}

        try:
            self.meta['value'].update(
                 { 'checksum': None,
                   'lastChecksumUpdated': None,
                   'checksumConflict': None,
                   'checkStatus': None })
            self.save()
        except Exception as e:
            exception_msg = 'Unable to initiate job. %s' % e
            logger.error(exception_msg)
            raise Exception(exception_msg)

        try:
            logger.debug("Job submission body: %s" % body)
            response = self._api_client.jobs.submit(body=body)
            logger.debug("Job submission response: %s" % response['id'])
        except Exception as e:
            exception_msg = 'Unable to initiate job. %s' % e
            logger.error(exception_msg)
            raise Exception(exception_msg)

        return response


# questions:
#   * create all objects with user client (particular client determined in the view)?
#   * share with system agave user to make public? - maybe share with ids user to begin with
#       - remember, all project objects need to be shared, including future objects after a project is made public
#   * webhook? not initiated by user... that's fine, we're going to update checksum as system client
#       - the bug we found will need to be fixed... and it is
#   * no public flag? - if we share everything with the system user, we will need a public flag
#       - maybe silly question but is there any sense in doing this: name=idsv.project.public? No, that's silly
#       - published better than public
#       - additional flags at project level:
#           '_published' t/f
#           '_has_unpublished' t/f
#           don't automatically publish new stuff
#           show new stuff that could be published project detail view
#   * scenerio, we have a new view for public projects (we also have a view for private projects)
#     the user clicks 'view' on a public project (that the user doesn't own). the app routes the user to /project/uuid
#       - how does the project-detail view know that the project is a public project not owned by the user?
#           try user client first? if not, try system client? see table below
#
#       - should we have separate views for public projects? /project/public/uuid? No, don't like it
#   * how do we list Specimens, Processes, Data, if there is no heirarchy (other than everything a child of Project)?
#       - is there actually a 'dynamic' heirarchy? dependent on the type of project?
#       - how would that work?

# need to go to view to edit
# put delete button in the edit view

#           which client to use?
#                   portal  |   user
# list public           X   |
# my projects               |   X
# view any models       X   |   ?        // read first with portal, fallback to user
# add/update                |   X
# webhook callback      X   |            // only write that we do as the portal client
# list systems              |   X
# list files                |   X
