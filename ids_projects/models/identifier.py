from base_metadata import BaseMetadata
import logging

logger = logging.getLogger(__name__)


class Identifier(BaseMetadata):
    name ='idsvc.identifier'

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
            id_type         # type of identifier ('DOI','SRA', etc.)
            uid             # unique external identifer (e.g. doi:10.1000/182)
        Explicit parameters take precedence over values found in the meta dictionary
        """
        super(Identifier, self).__init__(*args, **kwargs)

        self.id_type = kwargs.get('type')
        self.uid = kwargs.get('uid')
        self.dataset = kwargs.get('dataset')

        if self.id_type is not None:
            self.value.update({ 'id_type': self.id_type })

        if self.uid is not None:
            self.value.update({ 'uid': self.uid })

        if self.dataset is not None:
            self.add_association_to(self.dataset)

    @property
    def title(self):
        return self.value.get('id_type')

    @property
    def uid(self):
        return self.value.get('uid')

    @property
    def project(self):
        return next(iter([x for x in self.containers if x.name == 'idsvc.project']), None)

    @property
    def dataset(self):
        """Return the project for which this identifier was created"""
        return next(iter([x for x in self.containers if x.name == 'idsvc.dataset']), None)

    def delete(self):
        """ """
        if self.uuid is None:
            raise Exception('Cannot delete without UUID.')

            # remove dataset from containing objects (project)
            for container in self.containers:
                container.remove_part(self)
                container.save()

            # remove dataset as container from dataset's parts (data)
            for part in self.parts:
                part.remove_container(self)
                part.save()

        logger.debug('deleting identifier: %s - %s' % (self.title, self.uuid))
        self._api_client.meta.deleteMetadata(uuid=self.uuid)
        self.uuid = None