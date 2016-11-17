from base_metadata import BaseMetadata
from probe import Probe
import logging
import json

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


    def save(self):

        grouping = self.value.get('grouping', None)
        if grouping is not None:
            # (1) query probes with gene symbol == grouping

            query = {'name': 'idsvc.probe', 'value.gene_symbol': grouping}
            probes = self._api_client.meta.listMetadata(q=json.dumps(query))

            # (2) we want to get processes that those probes are input to

            processes = list()

            for probe_meta in probes:
                probe = Probe(api_client=self._api_client, meta=probe_meta)
                processes.extend(probe.processes)

            # (3) get data that is output of those processes

            grouped_data = list()

            for process in processes:
                grouped_data.extend(process.outputs)

            # (4) relate data to dataset (part)

            for data in grouped_data:
                self.add_part(data)
                super(Dataset, self).save()

                data.add_container(self)
                data.save()

        super(Dataset, self).save()


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
