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
