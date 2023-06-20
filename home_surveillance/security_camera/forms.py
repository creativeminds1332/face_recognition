from django import forms
from security_camera.models import face_dataset

class facedatasetForm(forms.ModelForm):
    class Meta:
        model=face_dataset
        fields=('face_name','image')
