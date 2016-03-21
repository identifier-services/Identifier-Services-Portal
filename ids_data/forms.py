from django import forms

class DataForm(forms.Form):
    system_id = forms.CharField(max_length=255)
    path = forms.CharField(max_length=255)

class DirectoryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        contents = kwargs.pop('contents')
        super(DirectoryForm, self).__init__(*args, **kwargs)
        self.fields["contents"] = forms.ChoiceField(widget=forms.RadioSelect, choices=contents)
