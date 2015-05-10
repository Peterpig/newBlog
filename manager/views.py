# coding=utf-8
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from common.form import BlogForm, PasswordForm, PicTypeForm, MypicForm

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


def manage(request):
    """
    ---------------------------------------
    功能说明：网站后台
    ---------------------------------------
    时间:     2015－04－10
    ---------------------------------------
    """	
    context = {}
    user = request.user

    return render(request, 'manager/manage.html', context)


def addBlog(request):
    """
    ---------------------------------------
    功能说明：添加博客
    ---------------------------------------
    时间:     2015－04－10
    ---------------------------------------
    """ 
    context = {}
    now = datetime.datetime.now()
    user = request.user
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            formData = form.cleaned_data
            title = formData.get('title')
            pwd = formData.get('is_show', '')
            content = formData.get('content')
            type = formData.get('type')
            tags = request.POST.get('id_tag', '')
            obj = int(request.POST.get('edit_or_creat', 0))    # 编辑还是创建
            now = datetime.datetime.now()

            # 保存theme
            # 将markdown格式转换纯文本

            from markdown import markdown
            html = markdown(content)
            rss = ''.join(BeautifulSoup(html).findAll(text=True))  # rss订阅源
            if len(content) > 500:
                html = markdown(content[:500])
            summary = ''.join(BeautifulSoup(html).findAll(text=True))

            if obj:     # 编辑状态
                blog = Blog.objects.filter(id=obj).update(title=title, type=int(type), summary=summary,rss=rss, content=content, content_show=html, add_date=now, is_show=pwd)
                blog = Blog.objects.get(id=obj)
            else:
                blog = Blog.objects.create(
                    title=title, type=int(type), summary=summary, rss=rss, content=content, add_date=now, is_show=pwd
                )
            # 博客导图
            img = getPic(blog.content_show)
            blog.img = img
            blog.save()

            if tags:
                tags = json.loads(tags)
                tag_list = []
                for i in tags:
                    i = i.strip()
                    if i and not Tag.objects.filter(name__iexact=i).exists():
                        tag = Tag.objects.create(name=i)
                        tag_list.append(tag)
                    elif i:
                        tag_list.append(Tag.objects.filter(name__iexact=i)[0])

                if obj:     # 编辑状态
                    BlogTag.objects.filter(blog=blog).delete()
                # 创建ThemeTag
                for i in tag_list:
                    BlogTag.objects.create(blog=blog, tag=i)

            return HttpResponseRedirect('/')

        context['form'] = form
        return render(request, 'manager/addtheme.html', context)
    else:
        id = request.GET.get('id', None)
        context['form'] = BlogForm()
        is_edit = 0
        if id:      # 编辑状况
            is_edit = id
            blog = get_object_or_404(Blog, pk=int(id))
            context['form'] = BlogForm(instance=blog)
            context['has_tags'] = BlogTag.objects.filter(blog=blog)
        codes = Type.objects.all().order_by('-id')
        tags = Tag.objects.all().order_by('-id')
        context['codes'] = codes
        context['tags'] = tags
        context['is_edit'] = is_edit
    return render(request, 'manager/addtheme.html', context)


def addType(request):
    """
    ---------------------------------------
    功能说明：添加分类
    ---------------------------------------
    时间:    2015－04－20
    ---------------------------------------
    """ 
    user = request.user
    if request.method == 'POST':
        name = request.POST.get('name').strip().lower()
        if not Type.objects.filter(name__iexact=name).exists():
            c_id = Type.objects.create(name=name).id
            return ajax.ajax_ok(c_id)


def getPic(html):
    """
    ---------------------------------------
    功能说明：获取博客导图
    ---------------------------------------
    时间:    2015－04－27
    ---------------------------------------
    """
    # 获取文章中的图片，如果有：抓取图片url 。否则使用本地图片
    soup = BeautifulSoup(html)
    s = soup.find('img')
    if s:
        return s['src']
    return '/site_media/img/blog/%s.jpg' % (random.choice(range(1, 10)))


def CreatePicType(request):
    """
    ---------------------------------------
    功能说明：创建图片类型
    ---------------------------------------
    时间:    2015－04－30
    ---------------------------------------
    """
    context = {}
    if request.method == 'POST':
        id = int(request.POST.get('id', 0))
        if id:
            pictype = get_object_or_404(PicType, pk=id)
            form = PicTypeForm(request.POST, instance=pictype)
        else:
            form = PicTypeForm(request.POST)
        if form.is_valid:
            f = form.save(commit=False)
            img = request.POST.get('pid')
            f.img = img
            f.save()
            return HttpResponseRedirect('/pic/')
        context['form'] = form
    else:
        id = request.GET.get('id', None)
        form = PicTypeForm()
        if id:
            pictype =get_object_or_404(PicType, pk=id)
            context['img_obj'] = pictype.getPic()
            form = PicTypeForm(instance=pictype)
        context['form'] = form
        context['id'] = id

    return render(request, 'pic/addtype.html', context)



def UploadPic(request):
    """
    ---------------------------------------
    功能说明：上传图片到七牛
    ---------------------------------------
    时间:    2015－05－07
    ---------------------------------------
    """
    if request.method == 'POST':
        img = request.FILES.get('Filedata', None)
        type = request.POST.get('type', None)
        if type:
            qn = SuperQiniu(img, w=800, h=520)
        else:
            qn = SuperQiniu(img)
        qn.uploadFile()
        remote_url = qn.downloadFile()
        key = qn.getKey()
        pic = Pic.objects.create(img=remote_url, key=key)
        return ajax.ajax_ok({'id':pic.id, 'url':pic.img, 'key':key})


def picView(request, id):
    """
    ---------------------------------------
    功能说明：展示相册中的照片
    ---------------------------------------
    时间:    2015－05－07
    ---------------------------------------
    """
    context = {}
    context['type'] = PicType.objects.get(pk=id)
    context['pics'] = MyPic.objects.filter(type=id).order_by('-id')
    return render(request, 'pic/pic.html', context)


def UploadMyPic(request, id):
    """
    ---------------------------------------
    功能说明：上传图片到我的相册
    ---------------------------------------
    时间:    2015－05－10
    ---------------------------------------
    """
    context = {}
    if request.method == 'POST':
        data = request.POST.get('data')
        data = json.loads(data)
        for obj in data:
            MyPic.objects.creat(type=id, img=obj['pid'], desc=obj['desc'])
        return HttpResponse('ok')
    else:
        pictype = get_object_or_404(PicType, pk=id)
        context['pictype'] = pictype

    return render(request, 'pic/addpic.html', context)