from django import forms
from django.forms import ModelForm

from .models import Scan


class ScanForm(ModelForm):

    class Meta:
        model = Scan
        fields = [
            'name', 'scan_file',
        ]
