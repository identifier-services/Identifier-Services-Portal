from django import forms

class ProjectForm(forms.Form):
    title = forms.CharField(max_length=255)
    GENOMIC = 'Genomic'
    INV_TYPES = (
        ('', 'Choose One'),
        (GENOMIC,GENOMIC),
    )
    investigation_type = forms.ChoiceField(choices=INV_TYPES, required=True)
    description = forms.CharField(max_length=255, widget=forms.Textarea, required=False)
