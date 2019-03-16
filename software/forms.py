from django import forms
from . models import UploadSoftware

class addSoftwareForm(forms.Form):
    software_id = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Software ID',
    }))

    software_title = forms.CharField(required=False,widget=forms.TextInput(attrs={
            'class' : 'form-control',
            'placeholder' : 'Software Title',
        }))

    software_file_size = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Software File Size',
    }))

    destination_path = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder': 'Destination Path',
    })) 

    source_location = forms.FileField(required=False,widget=forms.ClearableFileInput(attrs={
        'placeholder' : 'Store Path'
    }))
