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

        return title

    @property
    def project(self):
        return next(iter([x for x in self.my_associations if x.name == 'idsvc.project']), None)

    @property
    def specimen(self):
        return next(iter([x for x in self.my_associations if x.name == 'idsvc.specimen']), None)

    @property
    def data(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.data']

    @property
    def inputs(self):
        return [x for x in self.data if x.uuid in self.value['_inputs']]

    @property
    def outputs(self):
        return [x for x in self.data if x.uuid in self.value['_outputs']]

    def add_input(self, data):
        associations_to_me = self.associations_to_me
        associations_to_me.append(data)
        # necessary?
        self.associations_to_me = associations_to_me
        #
        inputs = self.inputs
        inputs.append(data)
        # necessary?
        self.inputs = inputs
        #
        self.add_association_from(data)

    def add_input(self, data):
        associations_to_me = self.associations_to_me
        associations_to_me.append(data)
        # necessary?
        self.associations_to_me = associations_to_me
        #
        outputs = self.outputs
        outputs.append(data)
        # necessary?
        self.outputs = outputs
        #
        self.add_association_from(data)
