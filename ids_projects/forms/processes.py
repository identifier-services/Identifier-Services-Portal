from django import forms
from .base import DynamicForm
from ..models import Process
import logging

logger = logging.getLogger(__name__)


class AddRelationshipForm(forms.Form):
    specimen_choices = forms.ChoiceField(label='Select Specimen',
                                         widget=forms.RadioSelect,
                                         required=True,
                                         help_text='Select specimen to relate to process.')

    def __init__(self, choices, *args, **kwargs):
        super(AddRelationshipForm, self).__init__(*args, **kwargs)
        self.fields['specimen_choices'].choices = choices

        try:
            for key in self.initial['value'].iterkeys():
                if key in self.fields:
                    self.fields[key].initial = self.initial['value'][key]
        except KeyError:
            logger.debug('New form, no initial values.')


class ProcessTypeForm(forms.Form):
    process_type = forms.ChoiceField()

    def __init__(self, choices, *args, **kwargs):
        super(ProcessTypeForm, self).__init__(*args, **kwargs)
        self.fields['process_type'].choices = choices


class ProcessFieldsForm(DynamicForm):
    metadata_model = Process
