from base_metadata import BaseMetadata
import logging

logger = logging.getLogger(__name__)


class Material(BaseMetadata):
    """ """
    name = 'idsvc.material'

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
        super(Material, self).__init__(*args, **kwargs)

    @property
    def material_type(self):
        return self.value.get('material_type')

    @property
    def title(self):
        title = self.value.get('material_type')
        return title.title()

    @property
    def project(self):
        return next(iter([x for x in self.containers if x.name == 'idsvc.project']), None)

    @property
    def processes(self):
        return next(iter([x for x in self.containers if x.parts == 'idsvc.process']), None)

    def add_project(self, project):
        """ """
        self.add_container(project)

    def add_process(self, process):
        """ """
        self.add_part(process)

    def delete(self):
        """ """
        if self.uuid is None:
            raise Exception('Cannot delete without UUID.')

        # delete all objects that have this object's uuid in their associationIds
        for container in self.containers:
            container.remove_part(self)
            container.save()

        for part in self.parts:
            logger.debug('Calling delete on {}: {} - {}'.format(part.name, part.uuid, part.title))
            part.delete()

        logger.debug('deleting material entity: %s - %s' % (self.title, self.uuid))

        try:
            self._api_client.meta.deleteMetadata(uuid=self.uuid)
        except Exception as e:
            logger.debug('Object does not exist, probably previously deleted. Error: %s' % e)

        self.uuid = None