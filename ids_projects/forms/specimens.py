from django import forms

class SpecimenForm(forms.Form):
    taxon_name = forms.CharField(max_length=255, required=True)
    specimen_id = forms.CharField(max_length=255, required=True)
    organ_or_tissue = forms.CharField(max_length=255)
    developmental_stage = forms.CharField(max_length=255)
    haploid_chromosome_count = forms.CharField(max_length=255)
    ploidy = forms.CharField(max_length=255)
    propogation = forms.CharField(max_length=255)
    estimated_genome_size = forms.CharField(max_length=255)
