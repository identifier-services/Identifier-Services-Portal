from django import forms

class ProjectForm(forms.Form):
    title = forms.CharField(max_length=255)
    SEQUENCING = 'Sequencing'
    ALIGNMENT = 'Alignment'
    REQUESTED = 'Requested'
    INV_TYPES = (
        ('', 'Choose One'),
        (SEQUENCING,SEQUENCING),
        (ALIGNMENT,ALIGNMENT),
    )
    investigation_type = forms.ChoiceField(choices=INV_TYPES, required=True)
    description = forms.CharField(max_length=255, widget=forms.Textarea, required=False)

class Specimen(forms.Form):
    title = forms.CharField(max_length=255)
    description = forms.CharField(max_length=-1, widget=forms.Textarea, required=False)

# class SystemForm(forms.Form):
#     def __int__(self, *args, **kwargs):
#         systems = kwargs.pop('systems')
#         self.fields['system'] = forms.ChoiceField(choices=systems, required=True)
#         super(SystemForm, self).__init__(*args, **kwargs)

class SystemForm(forms.Form):
    def __init__(self, systems,  *args, **kwargs):
        super(SystemForm, self).__init__(*args, **kwargs)
        self.fields["system"] = forms.ChoiceField(widget=forms.RadioSelect, choices=systems)
