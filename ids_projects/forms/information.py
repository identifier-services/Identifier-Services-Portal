from django import forms
from .base import DynamicForm
from ..models import Information
import logging

logger = logging.getLogger(__name__)


class AddRelationshipForm(forms.Form):
    process_choices = forms.ChoiceField(label='Select Process',
                                         widget=forms.RadioSelect,
                                         required=True,
                                         help_text='Select process to relate to information entity.')

    def __init__(self, choices, *args, **kwargs):
        super(AddRelationshipForm, self).__init__(*args, **kwargs)
        self.fields['process_choices'].choices = choices

        try:
            for key in self.initial['value'].iterkeys():
                if key in self.fields:
                    self.fields[key].initial = self.initial['value'][key]
        except KeyError:
            logger.debug('New form, no initial values.')


class InformationTypeForm(forms.Form):
    information_type = forms.ChoiceField()

    def __init__(self, choices, *args, **kwargs):
        super(InformationTypeForm, self).__init__(*args, **kwargs)
        self.fields['information_type'].choices = choices


class InformationFieldsForm(DynamicForm):
    metadata_model = Information
