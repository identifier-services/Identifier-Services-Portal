import logging
from django import forms


logger = logging.getLogger(__name__)


def _construct_form_field(f):
    field_class_name    = f.get('field_class', 'CharField')
    field_id            = f.get('id', None)
    field_label         = f.get('label', field_id)
    widget              = f.get('widget', 'TextInput')
    choices             = f.get('choices', None)
    required            = f.get('required', None)
    field_class         = getattr(forms, field_class_name)
    if choices:
        choices_tuple = tuple([(x,x) for x in choices])
        return forms.ChoiceField(label=field_label,
                                 choices=choices_tuple,
                                 required=required)
    else:
        return field_class(label=field_label,
                           widget=getattr(forms, widget),
                           required=required)


class ProcessTypeForm(forms.Form):
    process_type = forms.ChoiceField()

    def __init__(self, choices, *args, **kwargs):
        super(ProcessTypeForm, self).__init__(*args, **kwargs)
        self.fields['process_type'].choices = choices


class ProcessFieldsForm(forms.Form):

    def __init__(self, fields, *args, **kwargs):
        super(ProcessFieldsForm, self).__init__(*args, **kwargs)
        for f in fields:
            self.fields[f['id']] = _construct_form_field(f)
