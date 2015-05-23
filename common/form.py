# coding=utf-8
import random
import string
from PIL import Image

from django import forms
from django.forms import ModelForm
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from mysite.models import Type, Blog, Wiki, PicType, MyPic, Words, BlogDetal
from wmd.widgets import MarkDownInput   # 从wmd编辑器导入html组件


class Register(forms.Form):
    """
    ---------------------------------------
    功能说明：修改密码表单
    ---------------------------------------
    时间:     2015－04－17
    ---------------------------------------
    """
    username = forms.CharField(label=u'账号', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': u'账号(5-12位)', 'required':''}
        )
    )
    password1 = forms.CharField(label=u'密码', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': u'密码长度在5-12位', 'required':''}
        )
    )
    password2 = forms.CharField(label=u'再输入一次', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': u'再输入一次', 'required':''}
        )
    )

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        self.username = None
        self.user_name = None
        self.password1 = None
        super(Register, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(Register, self).clean()
        username = cleaned_data.get("username")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if username:
            if not 4 < len(username) < 13:
                msg = u'账号要在5-12位之间'
                raise forms.ValidationError(msg)
            elif User.objects.filter(username=username).exists():
                msg = u'账号已存在'
                raise forms.ValidationError(msg)

        if password1 and password2:
            if password1 != password2:
                msg = u'两次密码输入不相同'
                raise forms.ValidationError(msg)
            elif not 4 < len(password1) < 13:
                msg = u'密码要在5-12位之间'
                raise forms.ValidationError(msg)

        return cleaned_data

    def create(self):
        """
        创建用户
        """
        cleaned_data = super(Register, self).clean()
        username = cleaned_data.get("username")
        password1 = cleaned_data.get("password1")
        User.objects.create_user(username=username, password=password1)


class LoginForm(forms.Form):
    """
    ---------------------------------------
    功能说明：表单登陆类
    ---------------------------------------
    时间:     2015－04－10
    ---------------------------------------
    """
    us = forms.CharField(label=u'用户名', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': u'用户名', 'required': '', 'autofocus': ''}
        ),
    )
    pwd = forms.CharField(label=u'密码', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': u'密码', 'required': ''}
        ),
    )
    auto_login = forms.BooleanField(label=u'记住密码', required=False, widget=forms.CheckboxInput(
        attrs={'value': 1}
        ),
    )


    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        self.auto_login = None
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        us = self.cleaned_data.get('us')
        password = self.cleaned_data.get('pwd')
        auto_login = self.cleaned_data.get('auto_login', None)

        if us and password:
            if not User.objects.filter(username=us).exists():
                raise forms.ValidationError(u'该账号不存在！')
            self.user_cache = authenticate(username=us, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(u'邮箱或密码错误！')
            elif not self.user_cache.is_active:
                raise forms.ValidationError(u'该账号已被禁用！')
        # 自动登陆
        if auto_login:
            self.auth_login = True

        return self.cleaned_data

    def get_user_id(self):
        """
        获取用户id
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
        是否勾选了自动登陆
        """
        return self.auto_login

    def get_user_is_first(self):
        """
        判断用户是否为第一次登陆
        """
        is_first = False
        if self.user_cache and self.user_cache.type == -1:
            is_first = True
            self.user_cache.save()
        return is_first


class BlogForm(ModelForm):
    """
    ---------------------------------------
    功能说明：博客发布
    ---------------------------------------
    时间:     2015－04－10
    ---------------------------------------
    """
    title = forms.CharField(max_length=100, label=u'标题', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': u'标题', 'required': ''}
        )
    )
    type = forms.IntegerField()
    is_show = forms.CharField(required=False, max_length=100, label=u'加密', widget=forms.TextInput(
        attrs={'calss': 'form-control', 'placeholder': u'密码'}
        )
    )
    content = forms.CharField(label=u'内容', widget=MarkDownInput(
        attrs={'class': 'form-control', 'placeholder': u'内容', 'required': 'True'}
        )
    )

    class Meta:
        model = Blog
        fields = ('title', 'type', 'content', 'is_show')


class PasswordForm(forms.Form):
    """
    ---------------------------------------
    功能说明：修改密码表单
    ---------------------------------------
    时间:     2015－04－17
    ---------------------------------------
    """
    oldpwd = forms.CharField(label=u'原始密码', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': u'原始密码', 'required':''}
        )
    )
    password1 = forms.CharField(label=u'新密码', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': u'密码长度在5-12位', 'required':''}
        )
    )
    password2 = forms.CharField(label=u'再输入一次', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': u'再输入一次', 'required':''}
        )
    )

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        self.newpwd = None
        super(PasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(PasswordForm, self).clean()
        oldpwd = cleaned_data.get("oldpwd")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                msg = u'两次密码输入不相同'
                self._errors['password2'] = self.error_class([msg])
            if not 4 < len(password1) < 13:
                msg = u'密码要在5-12位之间'
                self._errors['password1'] = self.error_class([msg])
        return cleaned_data



class WikiForm(ModelForm):
    """
    ---------------------------------------
    功能说明：Wiki分类表单
    ---------------------------------------
    时间:     2015－04－19
    ---------------------------------------
    """
    content = forms.CharField(label=u'wiki', widget=MarkDownInput(
        attrs={'class': 'form-control', 'placeholder': u'wiki', 'required': ''})
    )

    class Meta:
        model = Wiki
        fields = ('content',)


class PicTypeForm(ModelForm):
    """
    ---------------------------------------
    功能说明：图片分类表单
    ---------------------------------------
    时间:     2015－04－19
    ---------------------------------------
    """
    title = forms.CharField(max_length=100, label=u'title', widget=forms.TextInput(
        attrs = {'class': 'form-control', 'placeholder': u'title', 'required': ''})
    )

    desc = forms.CharField(label=u'wiki', widget=forms.Textarea(
        attrs = {'class': 'form-control', 'placeholder': u'describe'})
    )

    def clean(self):
        cleaned_data = super(PicTypeForm, self).clean()
        title = cleaned_data.get('title').strip()
        if not title and PicType.objects.filter(title__incotains=title).exists():
            raise forms.ValidationError(u'该分类已存在！')
        return cleaned_data

    class Meta:
        model = PicType
        fields = ('title', 'desc')


class MypicForm(ModelForm):
    """
    ---------------------------------------
    功能说明：图片分类表单
    ---------------------------------------
    时间:     2015－04－19
    ---------------------------------------
    """
    type = forms.ModelChoiceField(queryset=PicType.objects.order_by('-id'), widget=forms.RadioSelect)

    desc = forms.CharField(label=u'wiki', widget=forms.Textarea(
        attrs= {'class': 'form-control', 'placeholder': u'describe'})
    )

    class Meta:
        model = MyPic
        fields = ('type', 'desc')


class BlogDetail(ModelForm):
    """
    ---------------------------------------
    功能说明：设置博客的网址等。增加可移植性、更好的SEO
    ---------------------------------------
    时间:     2015－05－19
    ---------------------------------------
    """

    blog_name = forms.CharField(max_length=50, label=u'博客名称', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': u'博客名称', 'required': ''}
        )
    )

    blog_title = forms.CharField(max_length=50, label=u'博客标题', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': u'博客标题', 'required': ''}
        )
    )

    blog_description = forms.CharField(max_length=300, label=u'博客描述', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': u'博客描述，用于百度等搜索引擎检索', 'required': ''}
        )
    )

    blog_keywords = forms.CharField(max_length=300, label=u'博客关键字', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': u'博客关键字，用于百度等搜索引擎检索', 'required': ''}
        )
    )

    blog_url = forms.CharField(max_length=100, label=u'网址', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': u'博客网址', 'required': ''}
        )
    )

    blog_tongji = forms.CharField(max_length=100, label=u'统计代码', widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': u'百度等统计代码！', 'required': ''}
        )
    )

    class Meta:
        model = BlogDetal
        fields = ('blog_name', 'blog_title', 'blog_description', 'blog_keywords', 'blog_url', 'blog_tongji')

