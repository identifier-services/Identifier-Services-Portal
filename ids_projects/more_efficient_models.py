import json

class BaseAgaveObject(object):
    """Anything that we want in all our Agave objects, contains only the api
    client at the moment."""
    def __init__(self, api_client, *args, **kwargs):
        # TODO: if type(api_client) is not agavepy.agave.Agave: raise Exception()
        self._api_client = api_client

class BaseMetadata(BaseAgaveObject):
    """Base class for IDS Metadata (Project, Specimen, Process, Data)"""
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

        # get meta if passed to constructor, convert to dict if necessary

        meta = kwargs.get('meta', {})
        if type(meta) is str:
            meta = json.loads(meta)
        self.load_from_meta(meta)

        # explicit constructor parameters take precedence over values found in
        # meta dictionary (namely 'uuid', and 'value' aka 'body')

        body = kwargs.get('body', meta.get('value', None))
        if type(body) is str:
            body = json.loads(body)
        self.body = body
        self.uuid = kwargs.get('uuid', meta.get('uuid', None))

        # create these instance variables for later

        self._upstream_objects = None
        self._downstream_objects = None

    def flush_associated(self):
        """Clears cached associated objects"""
        self._upstream_objects = None
        self._downstream_objects = None

    @property
    def upstream_objects(self):
        """Retrieves all metadata objects corresponding to this instance's associationIds"""
        if self._upstream_objects is None:
            query = { 'uuid': { '$in': self.associationIds } }
            self._upstream_objects = self._api_client.meta.listMetadata(q=json.dumps(query))

        return self._upstream_objects

    @property
    def downstream_objects(self):
        """Retrieves all metadata objects that have this instance's UUID in their associationIds"""
        if self._downstream_objects is None:
            query = { 'associationIds': self.uuid }
            self._downstream_objects = self._api_client.meta.listMetadata(q=json.dumps(query))

        return self._downstream_objects

    def load_from_meta(self, meta):
        """Set instance variables from dictionary or json"""
        if type(meta) is str:
            meta = json.loads(meta)

        self.uuid = meta.get('uuid', None)
        self.body = meta.get('value', None)
        self.owner = meta.get('owner', None)
        self.schemaId = meta.get('schemaId', None)
        self.internalUsername = meta.get('internalUsername', None)
        self.associationIds = meta.get('associationIds', None)
        self.lastUpdated = meta.get('lastUpdated', None)
        self.name = meta.get('name', None)
        self.created = meta.get('created', None)
        self._links = meta.get('_links', None)

    def load_from_agave(self):
        """Load metadata from tenant, if UUID is not None"""
        meta = self.user_ag.meta.getMetadata(uuid=self.uuid)
        self.load_from_meta(meta)

    def save(self):
        """Add or update metadata object on tenant"""

        if self.uuid is None:
            response = self._api_client.meta.addMetadata(body=self.meta)
        else:
            response = self._api_client.meta.updateMetadata(uuid=self.uuid, body=self.meta)
        self.load_from_meta(response)

        return response

    def delete(self):
        """Delete metadata object on tenant"""
        if self.uuid is None:
            raise Exception('Cannot delete without UUID.')

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

class Specimen(BaseMetadata):
    """ """
    name = 'idsvc.specimen'

    def __init__(self, *args, **kwargs):
        """ """
        super(Specimen, self).__init__(*args, **kwargs)

class Process(BaseMetadata):
    """ """
    name = 'idsvc.process'

    def __init__(self, *args, **kwargs):
        """ """
        super(Process, self).__init__(*args, **kwargs)

class Data(BaseMetadata):
    """ """
    name = 'idsvc.data'

    def __init__(self, *args, **kwargs):
        """ """
        super(Data, self).__init__(*args, **kwargs)

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
