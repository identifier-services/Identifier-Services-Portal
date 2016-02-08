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

class ProjectForm1(forms.Form):
    title = forms.CharField(max_length=255)
    description = forms.CharField(max_length=-1, widget=forms.Textarea, required=False)

class ProjectForm2(forms.Form):
    title = forms.CharField(max_length=255)
    description = forms.CharField(max_length=-1, widget=forms.Textarea, required=False)

class ProjectForm3(forms.Form):
    title = forms.CharField(max_length=255)
    description = forms.CharField(max_length=-1, widget=forms.Textarea, required=False)
