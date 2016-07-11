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
        self.value = {}
        self.owner = None
        self.schemaId = None
        self.internalUsername = None
        self.associationIds = None
        self._links = None
        self._my_associations = None
        self._associations_to_me = None

        # get 'meta' and 'uuid' arguments
        meta = kwargs.get('meta')
        uuid = kwargs.get('uuid')

        # if uuid is provided explicitly and meta is not, load object from
        # agave and return
        if meta is None:
            meta = { 'uuid': None, 'value': {} }
            if uuid is not None:
                self.uuid = uuid
                self.load_from_agave()
                return

        # get arguments
        # meta = kwargs.get('meta', { 'uuid': None, 'value': {} })
        value = kwargs.get('value')
        # uuid = kwargs.get('uuid')

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

            if associated_object in self.my_associations \
                and associated_object.uuid in self.associationIds:
                continue # skip, go on to next association

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

                if assoc_meta.name == 'idsvc.project':
                    assoc_object = Project(meta=assoc_meta, api_client=self._api_client)

                if assoc_meta.name == 'idsvc.specimen':
                    assoc_object = Specimen(meta=assoc_meta, api_client=self._api_client)

                if assoc_meta.name == 'idsvc.process':
                    assoc_object = Process(meta=assoc_meta, api_client=self._api_client)

                if assoc_meta.name == 'idsvc.data':
                    assoc_object = Data(meta=assoc_meta, api_client=self._api_client)

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

                if assoc_meta.name == 'idsvc.project':
                    assoc_object = Project(meta=assoc_meta, api_client=self._api_client)

                if assoc_meta.name == 'idsvc.specimen':
                    assoc_object = Specimen(meta=assoc_meta, api_client=self._api_client)

                if assoc_meta.name == 'idsvc.process':
                    assoc_object = Process(meta=assoc_meta, api_client=self._api_client)

                if assoc_meta.name == 'idsvc.data':
                    assoc_object = Data(meta=assoc_meta, api_client=self._api_client)

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
        self.associationIds = meta.get('associationIds', None)
        self._links = meta.get('_links', None)

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

    @classmethod
    def list(cls, api_client):
        """List idsvc objects accessible to the client"""
        query = {'name': cls.name}
        results = api_client.meta.listMetadata(q=json.dumps(query))

        if results is not None:
            return [cls(meta=r, api_client=api_client) for r in results]

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
                 'value': self.value,
                 '_links': self._links }

    def to_json(self):
        """The meta property, formatted as json string"""
        return json.dumps(self.meta)


class Project(BaseMetadata):
    """ """
    name = 'idsvc.project'

    def __init__(self, *args, **kwargs):
        """
        Required Parameter:
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
        super(Project, self).__init__(*args, **kwargs)

    @property
    def title(self):
        return self.value.get('title')

    @property
    def specimens(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.specimen']

    @property
    def processes(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.process']

    @property
    def data(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.data']

    @property
    def datasets(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.dataset']


class Specimen(BaseMetadata):
    """ """
    name = 'idsvc.specimen'

    def __init__(self, *args, **kwargs):
        """
        Required Parameter:
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
        super(Specimen, self).__init__(*args, **kwargs)

    @property
    def project(self):
        return next(iter([x for x in self.my_associations if x.name == 'idsvc.project']))

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
        """
        Required Parameter:
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
        super(Process, self).__init__(*args, **kwargs)

    @property
    def project(self):
        return next(iter([x for x in self.my_associations if x.name == 'idsvc.project']))

    @property
    def specimen(self):
        return next(iter([x for x in self.my_associations if x.name == 'idsvc.specimen']))

    @property
    def data(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.data']

    @property
    def inputs(self):
        return [x for x in self.data if x.uuid in self.value['_inputs']]

    @property
    def outputs(self):
        return [x for x in self.data if x.uuid in self.value['_outputs']]

    def add_input(self, data):
        associations_to_me = self.associations_to_me
        associations_to_me.append(data)
        # necessary?
        self.associations_to_me = associations_to_me
        #
        inputs = self.inputs
        inputs.append(data)
        # necessary?
        self.inputs = inputs
        #
        self.add_association_from(data)

    def add_input(self, data):
        associations_to_me = self.associations_to_me
        associations_to_me.append(data)
        # necessary?
        self.associations_to_me = associations_to_me
        #
        outputs = self.outputs
        outputs.append(data)
        # necessary?
        self.outputs = outputs
        #
        self.add_association_from(data)


class Data(BaseMetadata):
    """ """
    name = 'idsvc.data'

    def __init__(self, *args, **kwargs):
        """
        Required Parameter:
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
        super(Data, self).__init__(*args, **kwargs)

    @property
    def project(self):
        return next(iter([x for x in self.my_associations if x.name == 'idsvc.project']))

    @property
    def specimen(self):
        return next(iter([x for x in self.my_associations if x.name == 'idsvc.specimen']))

    @property
    def process(self):
        return next(iter([x for x in self.my_associations if x.name == 'idsvc.process']))

    @property
    def datasets(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.datasets']

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


class Dataset(BaseMetadata):
    name ='idsvc.dataset'

    def __init__(self, *args, **kwargs):
        """
        Required Parameter:
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
        super(Data, self).__init__(*args, **kwargs)

    @property
    def dataset_name(self):
        return self.value.get('dataset_name')

    @property
    def project(self):
        return next(iter([x for x in self.my_associations if x.name == 'idsvc.project']))

    @property
    def data(self):
        return [x for x in self.my_associations if x.name == 'idsvc.data']

    def add_data(self, data):
        datas = self.data
        datas.append(data)
        self.data = datas
        self.add_association_to(data)

    @property
    def identifiers(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.identifier']

    def add_identifier(self, identifier):
        identifiers = self.identifiers
        identifiers.append(identifier)
        self.identifiers = identifier
        self.add_association_from(identifier)


class identifier(BaseMetadata):
    name ='idsvc.identifier'

    def __init__(self, *args, **kwargs):
        """
        Required Parameter:
            api_client      # AgavePy client
        Optional Parameters:
            uuid            # unique identifier for existing metadata object
            body            # information held in metadata 'value' field
            meta            # json or dictionary, values may include:
                            #   uuid, owner, schemaId, internalUsername,
                            #   associationIds, lastUpdated, name, value,
                            #   created, _links
            id_type         # type of identifier ('DOI','SRA', etc.)
            uid             # unique external identifer (e.g. doi:10.1000/182)
        Explicit parameters take precedence over values found in the meta dictionary
        """
        super(Data, self).__init__(*args, **kwargs)

        self.id_type = kwargs.get('type')
        self.uid = kwargs.get('uid')
        self.dataset = kwargs.get('dataset')

        if self.id_type is not None:
            self.value.update({ 'id_type': self.id_type })

        if self.uid is not None:
            self.value.update({ 'uid': self.uid })

        if self.dataset is not None:
            self.add_association_to(dataset)

    @property
    def project(self):
        return next(iter([x for x in self.my_associations if x.name == 'idsvc.project']))

    @property
    def dataset(self):
        """Return the project for which this identifier was created"""
        return next(iter([x for x in self.my_associations if x.name == 'idsvc.dataset']))


class System(BaseAgaveObject):

    def __init__(self, *args, **kwargs):

        super(System, self).__init__(*args, **kwargs)
        self.id = None
        self.name = None
        self.type = None
        self.description = None
        self.status = None
        self.public = None
        self.default = None
        self._links = None

        # get 'meta' and 'uuid' arguments
        system_id = kwargs.get('system_id')
        meta = kwargs.get('meta')

        if meta is not None:
            self.load_from_meta(meta)

        if system_id is not None:
            self.id = system_id
            self.load_from_agave()

    def load_from_meta(self, meta):
        """Set instance variables from dictionary or json"""
        if type(meta) is str:
            meta = json.loads(meta)
        self.id = meta.get('id')
        self.name = meta.get('name')
        self.type = meta.get('type')
        self.description = meta.get('description')
        self.status = meta.get('status')
        self.public = meta.get('public')
        self.default = meta.get('default')
        self._links = meta.get('_links')

    @classmethod
    def list(cls, api_client, system_type="STORAGE"):
        """List systems available to the client.
        Required Parameter:
            api_client - AgavePy client object
        Optional parameter:
            system_type - ["STORAGE"(default)|"EXECUTION"]"""
        try:
            results = api_client.systems.list(type=system_type)
        except Exception as e:
            exception_msg = 'Unable to list systems. %s' % e
            logger.debug(exception_msg)
            raise e

        return [System(api_client=api_client, meta=meta) for meta in results]

    def listing(self, path):
        """List directory contents"""
        if not self.id:
            exception_msg = 'Missing system id, cannot list files.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        try:
            results = self._api_client.files.list(systemId=self.id, filePath=path)
            return results
        except Exception as e:
            exception_msg = 'Unable to list files. %s' % e
            logger.debug(exception_msg)
            raise e

    def load_from_agave(self):
        meta = self._api_client.systems.get(systemId=self.id)
        self.load_from_meta(meta)

    @property
    def meta(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'type' : self.type,
            'description' : self.description,
            'status' : self.status,
            'public' : self.public,
            'default' : self.default,
            '_links' : self._links,
        }


# TODO: make list a class method, and pass in api_client

# Notes 6/28:
# create any object with logged in user's client
# share with idsvc_user
# webhook will update using system
# when user publishes...
# tree will become public through flag
# ! no delete for public project !
# each view we check permission of logged in user for that thing only

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
