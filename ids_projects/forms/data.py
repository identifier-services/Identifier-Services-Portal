from django import forms
from .base import DynamicForm
from ..models import Data
import logging

logger = logging.getLogger(__name__)


class AddRelationshipForm(forms.Form):
    process_choices = forms.ChoiceField(label='Select Process',
                                         widget=forms.RadioSelect,
                                         required=True,
                                         help_text='Select process to relate to data.')

    input_output = forms.ChoiceField(label='As input or output?',
                                     choices = [('input','input'),('output','output')],
                                     widget=forms.RadioSelect,
                                     required=True,
                                     help_text='Is the data input or output to the process?')

    def __init__(self, choices, *args, **kwargs):
        super(AddRelationshipForm, self).__init__(*args, **kwargs)
        self.fields['process_choices'].choices = choices

        try:
            for key in self.initial['value'].iterkeys():
                if key in self.fields:
                    self.fields[key].initial = self.initial['value'][key]
        except KeyError:
            logger.debug('New form, no initial values.')


class DataTypeForm(forms.Form):
    data_type = forms.ChoiceField()

    def __init__(self, choices, *args, **kwargs):
        super(DataTypeForm, self).__init__(*args, **kwargs)
        self.fields['data_type'].choices = choices


class SRAForm(forms.Form):
    sra_id = forms.CharField(max_length=255)


class DataForm(DynamicForm):
    metadata_model= Data
