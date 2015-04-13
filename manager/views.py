# coding=utf-8
from django.shortcuts import render
from common.form import BlogForm,PasswordForm, PicTypeForm, MypicForm
from django.http import HttpResponseRedirect, HttpResponse
from mysite.models import Type, Tag, Blog, BlogTag, PicType, Pic, MyPic
from django.shortcuts import get_object_or_404
from common import ajax
import simplejson as json
import datetime
import random
import re, string
from common.superqiniu import SuperQiniu
from BeautifulSoup import BeautifulSoup
from markdown import markdown
