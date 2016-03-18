import logging
from django import forms


logger = logging.getLogger(__name__)


class SpecimenForm(forms.Form):
    taxon_name = forms.CharField(max_length=255, required=True)
    specimen_id = forms.CharField(max_length=255, required=True)
    organ_or_tissue = forms.CharField(max_length=255)
    developmental_stage = forms.CharField(max_length=255)
    haploid_chromosome_count = forms.CharField(max_length=255)
    ploidy = forms.CharField(max_length=255)
    propagation = forms.CharField(max_length=255)
    estimated_genome_size = forms.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        super(SpecimenForm, self).__init__(*args, **kwargs)
        try:
            for key in self.initial['value'].iterkeys():
                if key in self.fields:
                    self.fields[key].initial = self.initial['value'][key]
        except Exception as e:
            logger.debug('New project, no initial values.')
