#  注册
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# 创建form类
class RegForm(forms.Form):

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control username',
                                                             'placeholder': '用户名'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control password',
                                                             'placeholder': '密码'}))
    repeat_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control repeat_password',
                                                             'placeholder': '确认密码'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control email',
                                                             'placeholder': '邮箱'}))
    valid_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control valid',
                                                         'placeholder': '验证码'}))

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    # 自定义局部钩子，也就是规则，局部钩子只能给自己字段定义规则
    def clean_password(self):
        if len(self.cleaned_data['password']) > 8:  # self.cleaned_data['password']其实就是用户输入的密码的值
            return self.cleaned_data['password']
        else:
            raise ValidationError('密码小于8位')

    def clean_valid_code(self):
        if self.cleaned_data.get('valid_code') == self.request.session.get('valid_code'):
            return self.cleaned_data['valid_code']
        else:
            raise ValidationError('验证码输入错误！')

    # 定义全局钩子，全局钩子可以给多个字段定义规则
    def clean(self):
        if self.cleaned_data.get('password') == self.cleaned_data.get('repeat_password'):
            return self.cleaned_data
        else:
            raise ValidationError('密码不一致')
        # print(self.cleaned_data['password'])
        # print(self.cleaned_data['repeat_password'])
