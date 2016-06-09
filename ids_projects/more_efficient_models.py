import json

class BaseAgaveObject(object):
    """Anything that we want in all our Agave objects, contains only the api
    client at the moment."""
    def __init__(self, api_client, *args, **kwargs):
        # TODO: if type(api_client) is not agavepy.agave.Agave: raise Exception()
        self.api_client = api_client

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

        meta = kwargs.get('meta', {})
        self.load_from_meta(meta)

        # explicit parameters take precedence over values found in meta dictionary
        self.uuid = kwargs.get('uuid', meta.get('uuid', None))
        self.body = kwargs.get('body', meta.get('value', None))

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
            response = self.api_client.meta.addMetadata(body=self.meta)
        else:
            response = self.api_client.meta.updateMetadata(uuid=self.uuid, body=self.meta)
        self.load_from_meta(response)

    def delete(self):
        """Delete metadata object on tenant"""
        if self.uuid is not None:
            self.api_client.meta.deleteMetadata(uuid=self.uuid)
            self.uuid = None

    @property
    def meta(self):
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
#   * share with system agave user to make public?
#       - remember, all project objects need to be shared, including future objects after a project is made public
#   * no public flag?
#   * scenerio, we have a new view for public projects (we also have a view for private projects)
#     the user clicks 'view' on a public project (that the user doesn't own). the app routes the user to /project/uuid
#       - how does the project-detail view know that the project is a public project not owned by the user?
#       - should we have separate views for public projects? /project/public/uuid?
#   * how do we list Specimens, Processes, Data, if there is no heirarchy (other than everything a chile of Project)?
#       - is there actually a 'dynamic' heirarchy? dependent on the type of project?
#       - how would that work?
