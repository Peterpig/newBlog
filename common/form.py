#coding=utf-8

from django import forms
from django.forms import ModelForm
import random
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
#from mysite.models import Type, Blog, Wiki, PicType, MyPic, Words
from PIL import Image
import string
from wmd.widgets import MarkDownInput   # 从wmd编辑器导入html组件



class LoginForm(forms.Form):
    """
    功能说明: 表单登陆类
    ---------------------------------------
    修改人                    时间
    ---------------------------------------
    周培林                   2015－04－10
    """
    us = forms.CharField(label=u'用户名', max_length=100, widget=forms.TextInput(
            attrs={'class': 'forms-control', 'placeholder': u'用户名', 'required': '', 'autofocus': ''}
        ),
    )
    pwd = forms.CharField(label=u'密码',widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': u'密码', 'required': ''}
        )
    )
    auto_login = forms.BooleanField(label=u'记住密码',required=False,
        widget=forms.CheckboxInput(attrs={'value': 1}),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        self.auth_login = None
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        登陆验证
        """
        us = self.cleaned_data.get('us')
        password = self.cleaned_data.get('pwd')
        auth_login = self.cleaned_data.get('auth_login',None)

        if us and password:
            if not User.objects.filter(username=us).exists():
                raise forms.ValidationError(u'该账户不存在')

            self.user_cache = authenticate(username=us, password=password)

            if self.user_cache is None:
                raise forms.ValidationError(u'邮箱或密码错误！')
            elif not self.user_cache.is_active:
                raise forms.ValidationError(u'该账号已经被禁用！')

            if auth_login:          # 勾选自动登陆
                self.auth_login = True

            return self.cleaned_data

        def get_user_id(self):
            """
            获取用户ID
            """
            if self.user_cache:
                return self.user_cache.id
            return None

        def get_user(self):
            """
            获取用户实例
            """
            return self.user_cache

        def get_auto_login(self):
            """
            是否勾选自动登陆
            """
            return self.auth_login

        def get_user_is_first(self):
            """
            获取用户是否是第一次登陆
            """
            is_first = False
            if self.user_cache and self.user_cache.type == -1:
                is_first = True
                self.user_cache.save()
            return is_first
