from django import forms
import logging

logger = logging.getLogger(__name__)


class DynamicForm(forms.Form):

    def __init__(self, fields, *args, **kwargs):
        super(DynamicForm, self).__init__(*args, **kwargs)
        for f in fields:
            self.fields[f['id']] = self._construct_form_field(f)
        try:
            for key in self.initial['value'].iterkeys():
                if key in self.fields:
                    self.fields[key].initial = self.initial['value'][key]
        except Exception as e:
            logger.debug('No initial values.')

    class Meta:
        abstract = True

    def _construct_form_field(self, f):
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

    def save(self):
        instance = self.metadata_model()
        instance.value = self.cleaned_data
        instance.save()
