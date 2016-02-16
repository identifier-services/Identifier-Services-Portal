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

class DatasetForm(forms.Form):
    SEQUENCING = 'Sequencing'
    ALIGNMENT = 'Alignment'
    ANALYSIS = 'Anlysis'
    VAR_DETECT = 'Variant Detection'
    VAR_CALLING = 'Variant Calling'
    ANNOTATION = 'Annotation'
    GWAS = 'GWAS'
    OTHER = 'Other'
    PROC_TYPES = (
        ('', 'Choose One'),
        (SEQUENCING,SEQUENCING),
        (ALIGNMENT,ALIGNMENT),
        (ANALYSIS, ANALYSIS),
        (VAR_DETECT, VAR_DETECT),
        (VAR_CALLING, VAR_CALLING),
        (ANNOTATION, ANNOTATION),
        (GWAS, GWAS),
        (OTHER, OTHER),
    )
    process_type = forms.ChoiceField(choices=PROC_TYPES, required=True)
    seq_method = forms.CharField(max_length=255)
    seq_hardware = forms.CharField(max_length=255)
    assem_method = forms.CharField(max_length=255)
    ref_sequence = forms.CharField(max_length=255)
