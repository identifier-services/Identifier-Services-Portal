import logging
from django import forms
from .base import DynamicForm
import six

logger = logging.getLogger(__name__)


class ProcessTypeForm(forms.Form):
    process_type = forms.ChoiceField()

    def __init__(self, choices, *args, **kwargs):
        super(ProcessTypeForm, self).__init__(*args, **kwargs)
        self.fields['process_type'].choices = choices

class IdsMetadata(object):

    def __init__(self, uuid=None, *args, **kwargs):
        self.uuid = uuid
        self.value = {}
        self.created = None

        if self.uuid:
            ag = get_agave_client()
            meta = ag.meta.getMetadata(uuid=uuid)
            self.value = meta.value

    def get_associated(self, name=None, **kwargs):
        query = {
            'associationIds': [self.uuid]
        }
        if name:
            query['name'] = name

        for k, v in six.iteritems(kwargs):
            key = 'value.%s' % k
            query[key] = v

        ag = get_agave_client()
        return ag.meta.listMetadata(q=json.dumps(query))


class Process(IdsMetadata):
    name = 'idsvc.process'

    @property
    def data(self):
        if not self._data:
            self._data = self.get_associated(name='idsvc.data')

        return self._data

    @property
    def inputs(self):
        if not self._inputs:
            self._inputs = [d for d in self.data
                            if d.uuid in self.value.input_uuids]

        return self._inputs

    @property
    def outputs(self):
        if not self._outputs:
            self._outputs = [d for d in self.data
                            if d.uuid in self.value.output_uuids]

        return self._outputs

    def __init__(self, uuid=None, *args, **kwargs):
        super(Process, self).__init__(uuid, *args, **kwargs)

class ProcessFieldsForm(DynamicForm):

    metadata_model = Process

# p = Process(uuid='asdfasdfasdf')
#
# inputs = p.inputs
#
#
# p.get_associated(name='idsvc.data', type='sra_data')
# query = {
#     'name': 'idsvc.data',
#     'value.type': 'sra_data'
# }
