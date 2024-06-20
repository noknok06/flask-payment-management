from django import forms
from django.forms import ModelForm

from .models import Post


class DateInput(forms.DateInput):
    input_type = 'date'


class PostForm(ModelForm):

    parent_code = forms.IntegerField(label='親ポスト', required=False)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    class Meta:
        model = Post
        # views.pyファイルのfieldsと同じ。
        fields = ['status', 'contract_partner', 'category', 'title', 'tag', 'description', 'quotation_file','order_file',
                  'contract_method','contract_period_st', 'contract_period_fi', 
                  'order_date', 'recording_date', 'amount', 'reserve_fund',
                  'approval_flg', 'approval_data', 'asset_registration_flg', 'accrual_accounts', 'parent_code']
        widgets = {
            'recording_date': DateInput(),
            'order_date': DateInput(),
            'contract_period_st': DateInput(),
            'contract_period_fi': DateInput(),
        }

    def clean_parent_code(self):
        parent_code = self.cleaned_data.get('parent_code')
        if parent_code is not None:
            try:
                parent_post = Post.objects.get(pk=parent_code)
                return parent_post
            except Post.DoesNotExist:
                raise forms.ValidationError("指定された親ポストが存在しません。")
        return None