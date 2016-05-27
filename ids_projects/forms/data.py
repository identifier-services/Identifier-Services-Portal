from django import forms
from .base import DynamicForm
import logging

logger = logging.getLogger(__name__)


class DataTypeForm(forms.Form):
    data_type = forms.ChoiceField()

    def __init__(self, choices, *args, **kwargs):
        super(DataTypeForm, self).__init__(*args, **kwargs)
        self.fields['data_type'].choices = choices

class SRAForm(forms.Form):
    sra_id = forms.CharField(max_length=255)
