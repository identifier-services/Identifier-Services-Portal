from .base_metadata import BaseMetadata
import logging

logger = logging.getLogger(__name__)


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
        return [x for x in self.parts if x.name == 'idsvc.specimen']

    @property
    def processes(self):
        return [x for x in self.parts if x.name == 'idsvc.process']

    @property
    def data(self):
        return [x for x in self.parts if x.name == 'idsvc.data']

    @property
    def datasets(self):
        return [x for x in self.parts if x.name == 'idsvc.dataset']

    def add_specimen(self, specimen):
        """ """
        self.add_part(specimen)

    def add_process(self, process):
        """ """
        self.add_part(process)

    def add_data(self, data):
        """ """
        self.add_part(data)

    def add_dataset(self, dataset):
        """ """
        self.add_part(dataset)

    def delete(self):
        """Delete everything in the project"""
        if self.uuid is None:
            raise Exception('Cannot delete without UUID.')

        for part in self.parts:
            part.delete()

        logger.debug('deleting project: %s - %s' % (self.title, self.uuid))
        self._api_client.meta.deleteMetadata(uuid=self.uuid)
        self.uuid = None
