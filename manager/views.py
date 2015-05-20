# coding=utf-8
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from common.form import BlogForm, PasswordForm, PicTypeForm, MypicForm, BlogDetail

from mysite.models import Type, Tag, Blog, BlogTag, BlogDetal, PicType, Pic, MyPic
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
                    title=title, type=int(type), summary=summary, rss=rss, content=content, content_show=html, add_date=now, is_show=pwd
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
    try:        
        soup = BeautifulSoup(html)
        s = soup.find('img')
    except Exception, e:
        s = ""
    if s:
        return s['src']
    return '/site_media/img/blog/%s.jpg' % (random.choice(range(1, 10)))


def delBlog(request):
    """
    ---------------------------------------
    功能说明：删除博客
    ---------------------------------------
    时间:    2015－04－27
    ---------------------------------------
    """    
    if request.method == 'POST':
        id = request.POST.get('id')
        BlogTag.objects.filter(blog__id=id).delete()
        Blog.objects.filter(id=id).delete()
        return HttpResponse('ok')

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


def uploadBlog(request):
    """
    ---------------------------------------
    功能说明：上传博客
    ---------------------------------------
    时间:    2015－05－10
    ---------------------------------------
    """    
    context = {}
    now = datetime.datetime.now()
    if request.method == 'POST':
        type = request.POST.get('type')
        tags = request.POST.get('id_tag', '')
        file = request.POST.get('blog')
        context  = file.read().decode('utf-8').split('---', 2)
        content = [i for i in context if i]
        head = content[0]
        body = content[1]
        title = re.findall(r'title: .*', head)
        if title:
            title = title[0].split(':')[1].strip()
        else:
            title = u'一个神秘的标题'

        html = markdown(body)
        rss = ''.join(BeautifulSoup(html).findAll(text=True))   # rss订阅
        if len(body) > 500:
            html = markdown(body[:500])
        blog = Blog.objects.create(title=title, type=int(type), summary=summary, rss=rss, content=body, add_type=now)

        img = getPic(blog.content_show)         # 抓取本页中的图片然后返回。如果没有，使用已有的
        blog.img = img
        blog.save()
        if tags:
            tags = json.loads(tags)
            tag_list = []
            for i in tags:
                i = i.strip()
                if i and not Tag.objects.filter(name__iexact=i).exists():
                    tag = Tag.objects.creat(name=i)
                    tag_list.append(tag)
                elif i:
                    tag_list.append(Tag.objects.filter(name__iexact=i)[0])

            # 创建ThemeTag
            for i in tag_list:
                BlogTag.objects.create(blog=blog, tag=i)        
        return HttpResponse('/')
    context['types'] = Type.objects.order_by('-id')
    context['tags'] = Tag.objects.order_by('-id')
    return render(request, 'manager/uploadblog.html', context)


def changePwd(request):
    """
    ---------------------------------------
    功能说明：修改密码
    ---------------------------------------
    时间:    2015－05－18
    ---------------------------------------
    """
    context = {}        
    user = request.user
    context['form'] = PasswordForm()
    if request.method == 'POST':
        form = PasswordForm(user, request.POST)
        if form.is_valid():
            newpwd = form.cleaned_data.get('passsword1', None)
            if newpwd:
                user.set_password(newpwd)
                user.save()
                return HttpResponseRedirect('/')
        context['form'] = form
    return render(request, 'manager/pwd.html', context)


def blog_detail(request):
    """
    ---------------------------------------
    功能说明：博客标题、描述、关键字设置，用于SEO和改变博客名称
    ---------------------------------------
    时间:     2015－04－17
    ---------------------------------------
    """  
    context = {}
    user = request.user
    #context['form'] = BlogDetail()
    if request.method == 'POST':
        form = BlogDetail(user, request.POST)
        if form.is_valid():
            blog_name = request.POST.get('blog_name')
            blog_title = request.POST.get('blog_title')
            blog_description = request.POST.get('blog_description')
            blog_keywords = request.POST.get('blog_keywords')
            blog_url = request.POST.get('blog_url')
            blog_tongji = request.POST.get('blog_tongji')

            BlogDetal.objects.filter(pk=1).update(blog_name=blog_name,
                                                   blog_title=blog_title,
                                                   blog_description=blog_description,
                                                   blog_keywords=blog_keywords,
                                                   blog_url=blog_url,
                                                   blog_tongji=blog_tongji)
    else:
        
        detail = BlogDetal.objects.get(pk=1)
        row = {"blog_name":detail.blog_name, "blog_title":detail.blog_title, "blog_description":detail.blog_description, "blog_keywords":detail.blog_keywords, "blog_url":detail.blog_url, "blog_tongji":detail.blog_tongji}
        context['form'] = BlogDetail(row)
        print "context['form'] == ",context['form']

    return render(request, 'manager/blog_detail.html', context)