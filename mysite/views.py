#coding=utf-8
import simplejson as json

from common.form import LoginForm   #, WikiForm
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse

from mysite.models import *
#from common.superqiniu import SuperQiniu


def home(request):
    """
    ---------------------------------------
    功能说明：网站首页
    ---------------------------------------
    时间:     2015－04－10
    ---------------------------------------
    """
    context = {}
    context['blog'] = Blog.objects.order_by('-id')
    if request.method == 'GET':
        print "hehheh"
    return render(request, 'index.html', context)

def login_(request):
    """
    ---------------------------------------
    功能说明：登陆
    ---------------------------------------
    时间:     2015－04－10
    ---------------------------------------
    """
    context = {}
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()  # 获取用户实例
            if user:
                login(request, user)
                if form.get_auto_login():   # 设置session
                    request.session.set_expiry(None)
                return HttpResponseRedirect('/')
        context['form'] = form
    else:
        form = LoginForm()
        context['form'] = form
    return render(render, 'login.html', context)
def cus_500_err(request):
    return render(request, 'common/500.html')
