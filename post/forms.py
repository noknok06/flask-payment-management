from django import forms
from django.forms import ModelForm

from .models import Post


class DateInput(forms.DateInput):
    input_type = 'date'


class PostForm(ModelForm):

    class Meta:
        model = Post
        # views.pyファイルのfieldsと同じ。
        fields = ['contract_partner', 'category', 'title', 'description',
                  'contract_period_st', 'contract_period_fi', 'contract_method',
                  'order_date', 'recording_date',
                  'approval_flg', 'approval_data', 'status']
        widgets = {
            'recording_date': DateInput(),
            'order_date': DateInput(),
            'contract_period_st': DateInput(),
            'contract_period_fi': DateInput(),
        }
