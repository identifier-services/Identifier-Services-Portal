from base_metadata import BaseMetadata
import logging

logger = logging.getLogger(__name__)


class Probe(BaseMetadata):
    """ """
    name = 'idsvc.probe'

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
        super(Probe, self).__init__(*args, **kwargs)

    @property
    def title(self):
        probe_id = self.value.get('probe_id')
        gene_symbol = self.value.get('gene_symbol')
        accession_id = self.value.get('accession_id')

        title = "Probe: "
        title += probe_id if probe_id else ''
        title += ' ' + gene_symbol if gene_symbol else ''
        title += ' ' + accession_id if accession_id else ''

        return title

    @property
    def project(self):
        return next(iter([x for x in self.containers if x.name == 'idsvc.project']), None)

    @property
    def processes(self):
        return [x for x in self.is_input_to if x.name == 'idsvc.process']

    def add_project(self, project):
        """ """
        self.add_container(project)

    def add_process(self, process):
        """ """
        self.add_is_input_to(process)

    def delete(self):
        """ """
        if self.uuid is None:
            raise Exception('Cannot delete without UUID.')

        # delete all objects that have this object's uuid in their associationIds
        for container in self.containers:
            container.remove_part(self)
            container.save()

        for consumer in self.is_input_to:
            consumer.remove_is_input_to(self)
            consumer.save()

        logger.debug('deleting probe: %s - %s' % (self.title, self.uuid))

        try:
            self._api_client.meta.deleteMetadata(uuid=self.uuid)
        except Exception as e:
            logger.debug('Object does not exist, probably previously deleted. Error: %s' % e)

        self.uuid = None