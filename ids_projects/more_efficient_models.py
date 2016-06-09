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
        meta = self.user_ag.meta.getMetadata(uuid=self.uuid)
        self.load_from_meta(meta)

    def save(self):
        if self.uuid is None:
            response = self.api_client.meta.addMetadata(body=self.meta)
        else:
            response = self.api_client.meta.updateMetadata(uuid=self.uuid, body=self.meta)
        self.load_from_meta(response)

    def delete(self):
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
