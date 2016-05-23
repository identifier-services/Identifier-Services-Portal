import logging
from django import forms


logger = logging.getLogger(__name__)


class SRAForm(forms.Form):
    SRA_ID = forms.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        try:
            for key in self.initial['value'].iterkeys():
                if key in self.fields:
                    self.fields[key].initial = self.initial['value'][key]
        except Exception as e:
            logger.debug('New SRA, no initial values.')
