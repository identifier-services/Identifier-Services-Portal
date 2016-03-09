from django import forms
import logging


logger = logging.getLogger(__name__)


class ProjectForm(forms.Form):
    GENOMIC = 'Genomic'
    INV_TYPES = (
        ('', 'Choose One'),
        (GENOMIC,GENOMIC),
    )
    title = forms.CharField(max_length=255)
    investigation_type = forms.ChoiceField(choices=INV_TYPES, required=True)
    description = forms.CharField(max_length=255, widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        try:
            for key in self.initial['value'].iterkeys():
                if key in self.fields:
                    self.fields[key].initial = self.initial['value'][key]
        except Exception as e:
            logger.exception('Error parsing initial values in ProjectForm.')
