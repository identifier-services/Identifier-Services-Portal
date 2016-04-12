import logging
from django import forms


logger = logging.getLogger(__name__)

IDS_CONFIG = {
    'processes': [
        {
            'type': 'sequencing',
            'label': 'Sequencing',
            'fields': [
                {
                    'id': 'sequence_method',
                    'widget': 'Textarea'
                },
                {
                    'id': 'sequence_hardware',
                },
                {
                    'id': 'assembly_method',
                },
                {
                    'id': 'reference_sequence',
                },
            ]
        },
        {
            'type': 'alignment',
            'label': 'Alignment',
            'fields': [
                {
                    'id': 'homer_simpson'
                },
                {
                    'id': 'marge_simpson'
                },
                {
                    'id': 'bart_simpson'
                },
            ]
        }
    ]
}


def _construct_form_field(f):
    field_class_name = f.get('field_class', 'CharField')
    widget = f.get('widget', 'TextInput')
    choices = f.get('choices', None)
    field_class = getattr(forms, field_class_name)
    if choices:
        choice_tuple = tuple([(x,x) for x in choices])
        return field_class(choices=tuple([(x,x) for x in choices]))
    else:
        return field_class(widget=getattr(forms, widget))


class AProcessForm(forms.Form):
    process_type = forms.ChoiceField()

    def __init__(self, choices, *args, **kwargs):
        super(AProcessForm, self).__init__(*args, **kwargs)
        self.fields['process_type'].choices = choices


class BProcessForm(forms.Form):

    def __init__(self, fields, *args, **kwargs):
        super(BProcessForm, self).__init__(*args, **kwargs)
        for f in fields:
            # logger.debug(f)
            self.fields[f['id']] = _construct_form_field(f)


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

    # # hidden
    # project_uuid = forms.CharField(widget=forms.HiddenInput())
    # # maybe i should use MultiValueField?
    # associationIds = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ProcessForm, self).__init__(*args, **kwargs)
        try:
            for key in self.initial.iterkeys():
                if key in self.fields:
                    self.fields[key].initial = self.initial[key]
        except Exception as e:
            logger.debug('No initial process values.')
