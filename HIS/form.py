from django.forms import ModelForm, Form
from django import forms

from HIS.models import SickRecord, Issue

class SickRecordForm(ModelForm):
    birthday = forms.DateField(required=False, input_formats=['%Y/%m/%d'])
    care_date = forms.DateField(required=False, input_formats=['%Y/%m/%d'])
    sick_receive_date = forms.DateField(required=False, input_formats=['%Y/%m/%d'])
    class Meta:
        model = SickRecord
        exclude = ('issues','source_id',)

class IssueForm(ModelForm):
    class Meta:
        model = Issue

