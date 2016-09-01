from base_metadata import BaseMetadata
import logging

logger = logging.getLogger(__name__)


class Process(BaseMetadata):
    """ """
    name = 'idsvc.process'

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
        super(Process, self).__init__(*args, **kwargs)

        inputs = self.value.get('_inputs', [])
        outputs = self.value.get('_outputs', [])

        # creates input output items if they didn't exist
        self.value.update({'_inputs': inputs})
        self.value.update({'_outputs': outputs})

    @property
    def process_type(self):
        return self.value.get('process_type')

    @property
    def title(self):
        not_applicable = ('NA', 'N/A', 'NOT APPLICABLE', 'NONE', 'NULL')

        process_type = self.value.get('process_type')

        method = self.value.get('assembly_method',
                                self.value.get('sequencing_method',
                                               self.value.get('analysis_method', None)))

        if method in not_applicable:
            method = None

        title = process_type
        title += ' ' + method if method and method != process_type else ''

        return title.title()

    @property
    def project(self):
        return next(iter([x for x in self.containers if x.name == 'idsvc.project']), None)

    @property
    def specimen(self):
        return next(iter([x for x in self.containers if x.name == 'idsvc.specimen']), None)

    @property
    def data(self):
        return self.inputs + self.outputs

    def add_project(self, project):
        """ """
        self.add_container(project)

    def add_specimen(self, process):
        """ """
        self.add_container(process)

    def delete(self):
        """ """
        if self.uuid is None:
            raise Exception('Cannot delete without UUID.')

        # delete all objects that have this object's uuid in their associationIds
        for container in self.containers:
            container.remove_part(self)
            container.save()

        for part in self.parts:
            part.delete()

        for _input in self.inputs:
            _input.delete()

        for output in self.outputs:
            output.delete()

        logger.debug('deleting process: %s - %s' % (self.title, self.uuid))
        self._api_client.meta.deleteMetadata(uuid=self.uuid)
        self.uuid = None