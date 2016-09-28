from django import forms
from .base import DynamicForm
import logging

logger = logging.getLogger(__name__)


class UploadOptionForm(forms.Form):
    upload_option = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(UploadOptionForm, self).__init__(*args, **kwargs)
        self.fields['upload_option'].choices = [('Single','Single'), ('Bulk','Bulk')]


class UploadFileForm(forms.Form):
	file = forms.FileField(label='Select a file', help_text='max. 25MB')


