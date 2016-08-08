from django import forms
from .base import DynamicForm
from ..models import Dataset
import logging

logger = logging.getLogger(__name__)


class DataSelectForm(forms.Form):
    data_choices = forms.MultipleChoiceField(label='Select Data',
                                             widget=forms.CheckboxSelectMultiple,
                                             required=True,
                                             help_text='Select data to add to dataset.')

    def __init__(self, choices, *args, **kwargs):
        super(DataSelectForm, self).__init__(*args, **kwargs)
        self.fields['data_choices'].choices = choices

        try:
            for key in self.initial['value'].iterkeys():
                if key in self.fields:
                    self.fields[key].initial = self.initial['value'][key]
        except KeyError:
            logger.debug('New form, no initial values.')


class DatasetForm(DynamicForm):
    data_choices = forms.MultipleChoiceField(label='Select Data',
                                             widget=forms.CheckboxSelectMultiple,
                                             required=True,
                                             help_text='Select data to add to dataset.')

    metadata_model = Dataset

    def __init__(self, choices, *args, **kwargs):
        super(DatasetForm, self).__init__(*args, **kwargs)
        self.fields['data_choices'].choices = choices