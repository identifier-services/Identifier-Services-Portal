from .base_agave_object import BaseAgaveObject
import json, logging

logger = logging.getLogger(__name__)


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
        self._links = []

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
        self._links = meta.get('_links', [])

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
