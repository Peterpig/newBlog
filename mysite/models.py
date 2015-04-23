#coding=utf-8
from django.db import models
from wmd import models as wmd_models	# 导入wmd的models
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
import markdown


class Type(models.Model):
    """
    分类
    """
    name = models.CharField(max_length=50)
    add_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name
    def getCount(self):
        """
        获取分类数目
        """
        return Blog.objects.filter(type=self.id).count()

    class Meta:
        db_table = 'type'


class Blog(models.Model):
    """
    文章
    """
    title = models.CharField(max_length=100)
    type = models.IntegerField(default=0)
    img = models.CharField(max_length=500, null=True)	# 博客引导图片
    summary = models.CharField(max_length=500, null=True)
    rss = models.CharField(max_length=1024, null=True)	# rss订阅源
    content = wmd_models.MarkDownField()
    content_show = wmd_models.MarkDownField(u'正文显示',null=True)
    add_date = models.DateTimeField()
    counts = models.IntegerField(default=1)		# 点击率
    is_show = models.CharField(max_length=100, null=True)
    def __unicode__(self):
		return self.title

    class Meta:
        db_table = 'blog'

    def getType(self):
        """
        获取类型
        """
        return Type.objects.get(pk=self.type)

    def getTags(self):
        """
        获取标签
        """
        return BlogTag.objects.filter(blog=self.id)


class Tag(models.Model):
    """
    个人标签
    """
    name = models.CharField(max_length=100)
    add_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'tags'


class BlogTag(models.Model):
    """
    主题标签
    """
    blog = models.ForeignKey(Blog)
    tag = models.ForeignKey(Tag)
    add_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.tag.name

    class Meta:
        db_table = 'blog_tag'


class BlogDetal(models.Model):
    """
    ---------------------------------------
    功能说明：博客标题、描述、关键字设置，用于SEO和改变博客名称
    ---------------------------------------
    时间:     2015－04－17
    ---------------------------------------
    """
    blog_name = models.CharField(max_length=50)
    blog_title = models.CharField(max_length=50)
    blog_description = models.CharField(max_length=100)
    blog_keywords = models.CharField(max_length=300)
    blog_url = models.CharField(max_length=50)
    blog_tongji = models.CharField(max_length=500)

    def __unicode__(self):
        return self.blog_title

    class Meta:
        db_table = 'blogdetal'


class Pic(models.Model):
    """
    ---------------------------------------
    功能说明：博客图片
    ---------------------------------------
    时间:     2015－04－20
    ---------------------------------------
    """    
    img = models.CharField(max_length=200)
    key = models.CharField(max_length=200)  # 七牛key
    add_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pic'


class PicType(models.Model):
    """
    ---------------------------------------
    功能说明：博客缩略图
    ---------------------------------------
    时间:     2015－04－19
    ---------------------------------------
    """
    title = models.CharField(max_length=100)
    desc = models.CharField(max_length=500, null=True)
    add_time = models.DateTimeField(auto_now=True)
    img = models.IntegerField(null=True)    # 图片id

    def getPicCount(self):
        return MyPic.objects.filter(type=self.id).count()

    def getPic(self):
        return Pic.objects.get(pk=self.img)
    class Meta:
        db_table = 'pic_type'


class MyPic(models.Model):
    """
    ---------------------------------------
    功能说明：Mypic
    ---------------------------------------
    时间:    2015－04－19
    ---------------------------------------
    """    
    type = models.IntegerField()
    img = models.IntegerField(null=True)
    desc = models.CharField(max_length=500, null=True)
    add_date = models.DateTimeField(auto_now=True, auto_now_add=True)

    def getType(self):
        return PicType.objects.get(pk=self.type)

    def getPic(self):
        return Pic.objects.get(pk=self.img)

    class Meta:
        db_table = 'mypic'


class Word(models.Model):
    status = models.IntegerField(default=0) # 0:None; 1:Ok
    add_date = models.DateField(auto_now=True)

    class Meta:
        db_table = 'word'


class Words(models.Model):
    word = models.ForeignKey(Word)
    english = models.CharField(max_length=100)              # 0:None; 1:Ok
    explain = models.CharField(max_length=300, null=True)
    phonetic = models.CharField(max_length=100, null=True)   #  英标
    seq = models.CharField(max_length=300, null=True)
    add_time = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)   # ok

    class Meta:
        db_table = 'words'

class WikiType(models.Model):
    """
    ---------------------------------------
    功能说明：Wiki分类数据模型
    ---------------------------------------
    时间:    2015－04－19
    ---------------------------------------
    """
    name = models.CharField(max_length=50)
    add_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def getCount(self):
        """获取数目"""
        return Wiki.objects.filter(category=self.id).count()

    class Meta:
        db_table = 'wiki_type'


class Wiki(models.Model):
    """
    ---------------------------------------
    功能说明：Wiki数据模型
    ---------------------------------------
    时间:    2015－04－19
    ---------------------------------------
    """    
    category = models.IntegerField()
    content = wmd_models.MarkDownField()
    content_show = wmd_models.MarkDownField(u'show', null=True)
    add_time = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        db_table = 'wiki'

    def save(self, force_insert=False, force_update=False, using=None):
        self.content_show = mark_safe(markdown.markdown(force_unicode(self.content), ['codehilite'], safe_mode='escape'))
        super(Wiki, self).save()
