from django import forms


class DataForm(forms.Form):
    system_id = forms.CharField(max_length=255)
    path = forms.CharField(max_length=255)


class SystemForm(forms.Form):
    def __init__(self, *args, **kwargs):
        systems = kwargs.pop('systems')
        super(SystemForm, self).__init__(*args, **kwargs)
        self.fields["system"] = forms.ChoiceField(widget=forms.RadioSelect, choices=systems)
