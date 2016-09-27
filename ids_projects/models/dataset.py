from base_metadata import BaseMetadata
import logging

logger = logging.getLogger(__name__)


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
        super(Dataset, self).__init__(*args, **kwargs)

        self._project = None
        self._data = None
        self._identifiers = None

    @property
    def title(self):
        return self.value.get('dataset_name')

    @property
    def project(self):
        """Returns the project to which this dataset is assoicated"""
        # if self._project is None:
        #     project = next(iter([x for x in self.my_associations if x.name == 'idsvc.project']), None)
        #     self._project = project
        # return self._project
        return next(iter([x for x in self.containers if x.name == 'idsvc.project']), None)

    @property
    def data(self):
        """Returns the data grouped by this dataset"""
        # if self._data is None:
        #     data = [x for x in self.my_associations if x.name == 'idsvc.data']
        #     self._data = data
        # return self._data
        return [x for x in self.parts if x.name == 'idsvc.data']

    def add_to_project(self, project):
        """
        Add this dataset to an existing project, which should be passed as a parameter
        """
        self.add_container(project)

    def add_data(self, data):
        """ """
        self.add_part(data)

    @property
    def identifiers(self):
        return [x for x in self.parts if x.name == 'idsvc.identifier']

    def add_identifier(self, identifier):
        self.add_part(identifier)

    def delete(self):
        """Delete the dataset and erase relationships"""
        if self.uuid is None:
            raise Exception('Cannot delete without UUID.')

        # remove dataset from containing objects (project)
        for container in self.containers:
            logger.debug('removing part (%s): %s - %s, from container (%s): : %s - %s' %
                         (self.name, self.uuid, self.title, container.name, container.uuid, container.title))
            container.remove_part(self)
            container.save()

        # remove dataset as container from dataset's parts (data)
        for part in self.parts:
            logger.debug('removing container (%s): %s - %s, from part (%s): : %s - %s' %
                         (self.name, self.uuid, self.title, container.name, container.uuid, container.title))
            part.remove_container(self)
            part.save()

        logger.debug('deleting %s: %s - %s' % (self.name, self.uuid, self.title))
        self._api_client.meta.deleteMetadata(uuid=self.uuid)
        self.uuid = None