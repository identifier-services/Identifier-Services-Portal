from django import forms

class DataForm(forms.Form):
    system_id = forms.CharField(max_length=255)
    path = forms.CharField(max_length=255)
