from django import forms
from .base import DynamicForm
from ..models import Process
import logging

logger = logging.getLogger(__name__)


class ProcessTypeForm(forms.Form):
    process_type = forms.ChoiceField()

    def __init__(self, choices, *args, **kwargs):
        super(ProcessTypeForm, self).__init__(*args, **kwargs)
        self.fields['process_type'].choices = choices


class ProcessFieldsForm(DynamicForm):
    metadata_model = Process
