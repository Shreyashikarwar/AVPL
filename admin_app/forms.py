from ckeditor_uploader.widgets import CKEditorWidget, CKEditorUploadingWidget
from .models import *

class AboutForm(forms.ModelForm):
    class Meta:
        model = AboutUs
        fields = '__all__'