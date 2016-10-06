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

    @property
    def probes(self):
        return [x for x in self.parts if x.name == 'idsvc.probe']

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

    def add_probe(self, probe):
        """ """
        self.add_part(probe)

    def delete(self):
        """Delete everything in the project"""
        if self.uuid is None:
            raise Exception('Cannot delete without UUID.')

        for part in self.parts:
            logger.debug('Calling delete on {}: {} - {}'.format(part.name, part.uuid, part.title))
            part.delete()

        logger.debug('deleting %s: %s - %s' % (self.name, self.uuid, self.title))

        try:
            self._api_client.meta.deleteMetadata(uuid=self.uuid)
        except Exception as e:
            logger.debug('Object does not exist, probably previously deleted. Error: %s' % e)

        self.uuid = None

    def query_probes_by_id(self, probe_ids):        
        probes = []

        for probe_id in probe_ids:
                           
            # '{"name": "idsvc.probe", "value.probe_id": "R5001", "value._relationships": {"$elemMatch": {"@id": "1952466296496067046-242ac1111-0001-012"}}}'
            query = {}
            query['value._relationships'] =  {'$elemMatch': {'@id': self.uuid}}
            query['name'] = "idsvc.probe"
            query['value.probe_id'] = probe_id

            results = self.query_related_objects(query)

            if len(results) > 1:
                raise Exception('More than one probe is returned for probe id of %s' % probe_id)

            probes.extend(results)

        return probes

    def query_specimens_by_id(self, specimen_ids):
        specimens = []

        for specimen_id in specimen_ids:
            query = {}
            query['value._relationships'] =  {'$elemMatch': {'@id': self.uuid}}
            query['name'] = "idsvc.specimen"
            query['value.specimen_id'] = specimen_id

            results = self.query_related_objects(query)

            if len(results) > 1:
                raise Exception('More than one specimen is returned for specimen id of %s' % specimen_id)

            specimens.extend(results)

        return specimens



