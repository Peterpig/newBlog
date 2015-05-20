# coding=utf-8
import random
import simplejson as json

from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from common.form import LoginForm, WikiForm

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
    context['detals'] = get_blog_detals()
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
            user = form.get_user()      # 获取用户实例
            if user:
                login(request, user)
                if form.get_auto_login():   # 设置session
                    request.session.set_expiry(10)    # 设置过期时间
                return HttpResponseRedirect('/')
        context['form'] = form
    else:
        form = LoginForm()
        context['form'] = form
    return render(request, 'login.html', context)


def logout_(request):
    """
    ---------------------------------------
    功能说明：退出
    ---------------------------------------
    时间:     2015－04－10
    ---------------------------------------
    """
    logout(request)
    return HttpResponseRedirect('/')


def search(request):
    """
    ---------------------------------------
    功能说明：首页搜索模块
    ---------------------------------------
    时间:     2015－04－10
    ---------------------------------------
    """
    context = {}
    key = request.GET.get('search', '')
    context['key'] = key
    context['blogs'] = Blog.objects.filter(Q(title__icontains=key) | Q(content__icontains=key)).order_by('-id')     # 标题检索
    return render(request, 'search.html', context)


def sidebar(request):
    """
    ---------------------------------------
    功能说明：侧边栏，放置热门文章和标签云等
    ---------------------------------------
    时间:     2015－04－10
    ---------------------------------------
    """
    if request.method == 'POST':
        context = {}
        context['types'] = Type.objects.order_by('-id')          # 获取分类  id倒序
        context['tag'] = tagsCloud()                            # 标签云
        context['hot'] = Blog.objects.order_by('-counts')[:15]  # 热门文章 前15篇
        return render(request, 'common/sidebar.html', context)


def about(request):
    """
    ---------------------------------------
    功能说明：关于本站
    ---------------------------------------
    时间:     2015－04－10
    ---------------------------------------
    """
    return render(request, 'about.html')


def resume(request):
    """
    ---------------------------------------
    功能说明：关于本人
    ---------------------------------------
    时间:     2015－04－10
    ---------------------------------------
    """
    return render(request, 'resume/index.html')


def blog(request, id=None):
    """
    ---------------------------------------
    功能说明：博客详情页面
    ---------------------------------------
    时间:     2015－04－16
    ---------------------------------------
    """
    context = {}
    blog = Blog.objects.get(pk=id)
    if blog.is_show:
        # 博客加密，跳转到验证界面
        return HttpResponseRedirect('/ciphertext/%s/' % id)
    # 访问次数加一
    blog.counts += 1
    blog.save()
    context['blog'] = blog
    context['is_blog_view'] = True
    context['id'] = id
    # 上下一篇博客
    context['pn'] = get_neighbour(id)
    return render(request, 'blog.html', context)


def get_neighbour(id):
    """
    ---------------------------------------
    功能说明：获取上一篇、下一篇博客
    ---------------------------------------
    时间:     2015－04－16
    ---------------------------------------
    """
    id = int(id)
    blog_list = Blog.objects.values_list('id', flat=True).order_by('id')
    dic = {}
    blog_list = list(blog_list)
    if blog_list:
        id_index = blog_list.index(id)  # 当前id的索引
        pre, next = 0, 0

        if len(blog_list) > 1:
            # 如果不是第一篇或最后一篇
            if id_index != 0 and id_index != len(blog_list) - 1:
                pre = blog_list[id_index - 1]
                next = blog_list[id_index + 1]
            else:
                if id_index == 0:       # 第一篇
                    next = blog_list[id_index + 1]
                if id_index == len(blog_list) - 1:    # 最后一篇
                    pre = blog_list[id_index - 1]
        elif len(blog_list) == 1:
            pre, next = 0, 0
        dic = {'pre': pre, 'next': next}
    return dic


def tagsCloud():
    """
    ---------------------------------------
    功能说明：标签云.随机生成不同颜色的标签
    ---------------------------------------
    时间:     2015－04－10
    ---------------------------------------
    """
    tags = Tag.objects.all()
    tagscloud = []
    for obj in tags:
        size = random.randint(12, 30)   # 随机字体大小
        # 随机生成RGB
        R = random.randint(0, 254)
        G = random.randint(0, 254)
        B = random.randint(0, 254)
        RGB = 'rgb(%s,%s,%s)' % (R, G, B)

        dic = {}
        dic['name'] = obj.name
        dic['id'] = obj.id
        dic['size'] = size
        dic['rgb'] = RGB
        tagscloud.append(dic)
    return tagscloud


def blogType(request, id):
    """
    ---------------------------------------
    功能说明：获取指定分类的博客
    ---------------------------------------
    时间:     2015－04－10
    ---------------------------------------
    """
    context = {}
    context['type_name'] = Type.objects.get(pk=id).name
    context['blogs'] = Blog.objects.filter(type=id).order_by('-id')
    return render(request, 'blog_type.html', context)


def blogTag(request, id):
    """
    ---------------------------------------
    功能说明：博客标签检索
    ---------------------------------------
    时间:     2015－04－19
    -----
    """
    context = {}
    context['tag_name'] = Tag.objects.get(pk=id).name
    context['blogs'] = BlogTag.objects.filter(tag__id=id).order_by('-id')
    return render(request, 'blog_tag.html', context)


def get_blog_detals():
    """
    ---------------------------------------
    功能说明：获得网站标题、描述、关键字等
    ---------------------------------------
    时间:     2015－04－19
    ---------------------------------------
    """
    dic = {}
    detal = BlogDetal.objects.get(pk=1) or ''

    if detal:
        dic['name'] = detal.blog_name
        dic['title'] = detal.blog_title
        dic['description'] = detal.blog_description
        dic['keywords'] = detal.blog_keywords
        dic['url'] = detal.blog_url
        dic['tongji'] = detal.blog_tongji
    else:
        # 默认值
        dic['name'] = 'Anybfans'
        dic['title'] = 'Anybfans博客'
        dic['description'] = '享受编程的乐趣'
        dic['keywords'] = 'Anybfans,anybfans'
        dic['url'] = 'www.anybfans.com'

    return dic


def cus_500_err(request):
    return render(request, 'common/500.html')


def cus_404_err(request):
    return render(request, 'common/404.html')


def commonDel(request):
    """
    ---------------------------------------
    功能说明：删除文章
    ---------------------------------------
    时间:     2015－04－20
    ---------------------------------------
    """
    if request.method == "POST":
        str_model = request.POST.get('model')
        id = request.POST.get('id')
        obj_content = ContentType.objects.get(model=str_model)
        if str_model == 'pictype':          # delete pic
            img = []
            img += MyPic.objects.filter(type=id).values_list('img', flat=True)
            img.append(PicType.objects.get(pk=id).img)
            keys = Pic.objects.filter(id__in=img).values_list('key', flat=True)
            # delete remote file
            qn = SuperQiniu(keys)
            qn.delMoreFiles()
            # delete models
            MyPic.objects.filter(type=id).delete()
        if str_model == 'pic':
            MyPic.objects.filter(img=id).delete()
            PicType.objects.filter(img=id).delete()
            picture = Pic.objects.get(pk=id)
            qn = SuperQiniu(picture.key)
            qn.delFile()        # 删除远程图片
        """
        if str_model == 'wikitype':         # delete wiki
            Wiki.objects.filter(category=id).delete()
        """
        obj = obj_content.get_object_for_this_type(pk=id).delete()
        return HttpResponse('ok')


def wiki(request, id=None):
    """
    ---------------------------------------
    功能说明：wiki百科
    ---------------------------------------
    时间:     2015－04－21
    ---------------------------------------
    """
    context = {}
    print "id=",id
    context['wikiType'] = WikiType.objects.order_by('-id')
    if context['wikiType']:
        if not id:
            id = context['wikiType'][0].id
        context['id'] = id
        context['wiki'] = Wiki.objects.filter(category=id).order_by('-id')
    return render(request, 'wiki/wiki.html', context)


def wiki_add_type(request):
    """
    ---------------------------------------
    功能说明：添加wiki分类
    ---------------------------------------
    时间:     2015－04－22
    ---------------------------------------
    """   
    if request.method == 'POST':
        name = request.POST.get('name', '')
        id = int(request.POST.get('id', 0))
        name = name.strip()
        if id:
            # 编辑状态
            WikiType.objects.filter(pk=id).update(name=name)
            return HttpResponse('ok')
        if name and not WikiType.objects.filter(name__icontains=name):
            WikiType.objects.create(name=name)
            return HttpResponse('ok')
        else:
            # 分类存在
            return HttpResponse(0)


def wiki_add(request, id=None):
    """
    ---------------------------------------
    功能说明：添加wiki
    ---------------------------------------
    时间:     2015－04－22
    ---------------------------------------
    """  
    context = {}
    if id:
        context['typename'] = WikiType.objects.get(pk=id)
    if request.method == 'POST':
        wid = int(request.POST.get('id', 0))
        if wid:
            wiki_ = get_object_or_404(Wiki, pk=wid)
            form = WikiForm(request.POST, instance=wiki_)
        else:
            form = WikiForm(request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            f.category = id
            f.save()
            return HttpResponseRedirect('/wiki/%s' %id)
        context['form'] = form
    else:
        # GET请求
        id = request.GET.get('id', None)
        form = WikiForm()
        if id:
            wiki_ = get_object_or_404(Wiki, pk=id)
            form = WikiForm(instance=wiki_)     # 生成表单，同时填充内容
        context['form'] = form
        context['id'] = id

    return render(request, 'wiki/add.html', context)


def ciphertext(request, id=None):
    """
    ---------------------------------------
    功能说明：带密码的博文访问
    ---------------------------------------
    时间:     2015－05－04
    ---------------------------------------
    """ 
    if id and Blog.objects.filter(id=id).exists():
        blog = Blog.objects.get(pk=id)
        pwd = blog.is_show
        if request.method == 'POST':
            # 输入的密码
            in_pwd = request.POST.get('pwd', '')
            if in_pwd == pwd:
                context = {}
                blog.counts += 1
                blog.save()
                context['blog'] = blog
                context['is_blog_view'] = True
                context['id'] = id
                context['pn'] = get_neighbour(id)
                return render(request, 'blog.html', context)
        return render(request, 'common/ciphertext.html')
    return HttpResponseRedirect('/404/')


def commonDel(request):
    """models to delete"""
    if request.method == "POST":
        str_model = request.POST.get('model')
        id = request.POST.get('id')
        obj_content = ContentType.objects.get(model=str_model)
        if str_model == 'pictype':          # delete pic
            img = []
            img += MyPic.objects.filter(type=id).values_list('img', flat=True)
            img.append(PicType.objects.get(pk=id).img)
            keys = Pic.objects.filter(id__in=img).values_list('key', flat=True)
            # delete remote file
            qn = SuperQiniu(keys)
            qn.delMoreFiles()
            # delete models
            MyPic.objects.filter(type=id).delete()
        if str_model == 'pic':
            MyPic.objects.filter(img=id).delete()
            PicType.objects.filter(img=id).delete()
            picture = Pic.objects.get(pk=id)
            qn = SuperQiniu(picture.key)
            qn.delFile()        # 删除远程图片
        if str_model == 'wikitype':         # delete wiki
            Wiki.objects.filter(category=id).delete()

        obj = obj_content.get_object_for_this_type(pk=id).delete()
        return HttpResponse('ok')


def pic(request):
    """
    ---------------------------------------
    功能说明：获取博客导图
    ---------------------------------------
    时间:     2015－04－19
    -----
    """
    context = {}
    context['pics'] = PicType.objects.order_by('-id')
    return render(request, 'pic/index.html', context)


def picView(request, id):
    """
    ---------------------------------------
    功能说明：图册添加图片
    ---------------------------------------
    时间:     2015－05－10
    -----
    """    
    context = {}
    context['type'] = PicType.objects.get(pk=id)
    context['pics'] = MyPic.objects.filter(type=id).order_by('-id')
    return render(request, 'pic/pic.html', context)


def pigeonhole(request):
    """
    ---------------------------------------
    功能说明： 博客归档
    ---------------------------------------
    时间:     2015－05－12
    -----
    """      
    blogs = Blog.objects.values('id', 'title', 'add_date').order_by('-add_date')
    counts = len(blogs)
    dates = set([str(i['add_date'].year)+str(i['add_date'].month) for i in blogs])
    blogs_list = []
    for i in dates:
        dic = {}
        b_info = []
        count = 0
        dic['ym'] = i[:4]+u'年'+i[4:]+u'月'
        for obj in blogs:
            if str(obj['add_date'].year)+str(obj['add_date'].month) == i:
                dic_ = {}
                dic_['blog'] = "<a href='/blog/%s/'>%s</a>" %(obj['id'], obj['title'])
                b_info.append(dic_)
                count += 1
        dic['count'] = count
        dic['b_info'] = b_info
        blogs_list.append(dic)

    return render(request, 'common/pigeonhole.html', {'blogs_list':blogs_list, 'count':counts})