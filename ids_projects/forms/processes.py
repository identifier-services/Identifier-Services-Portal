from django import forms

class ProcessForm(forms.Form):
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
    sequence_method = forms.CharField(max_length=255)
    sequence_hardware = forms.CharField(max_length=255)
    assembly_method = forms.CharField(max_length=255)
    reference_sequence = forms.CharField(max_length=255)

    # hidden
    project_id = forms.CharField(widget=forms.HiddenInput())
    # maybe i should use MultiValueField?
    associationIds = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ProcessForm, self).__init__(*args, **kwargs)
        try:
            for key in self.initial.iterkeys():
                if key in self.fields:
                    self.fields[key].initial = self.initial[key]
        except Exception as e:
            logger.debug('No initial process values.')
