from django import forms


class ProjectForm(forms.Form):
    title = forms.CharField(max_length=255)
    description = forms.CharField(max_length=-1, widget=forms.Textarea, required=False)

