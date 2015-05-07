# coding = utf-8

import qiniu.conf
import qiniu.rs
import qiniu.io

import datetime
import StringIO	
from PIL import Image

from django.conf import settings

# 初始化七牛key
qiniu.conf.ACCESS_KEY = settings.QINIU_ACCESS_KEY
qiniu.conf.SECRET_KEY = settings.QINIU_SECRET_KEY

# 上传凭证
policy = qiniu.rs.PutPolicy(settings.QINIU_BUCKET_NAME)
uptoken = policy.token()


class ClassName(object):
    """
    ---------------------------------------
    功能说明：七牛图片上传类
    ---------------------------------------
    """	
	def __init__(self, filepath, w=200, h=200, required=None, **kwargs):
		self.filepath = filepath 	# 文件绝对路径
		self.key = datetime.datetime.now()
		self.required = required
		self.w = w 					# 图片宽度
		self.h = h 					# 图片高度
		self.kwargs = kwargs

	def uploadFile(self):
		"""上传图片方法"""
		extra = qiniu.io.PutExtra()
		mime_type = self.filepath.content_type
		extra.mime_type = mime_type
		type = 'PNG'
		if mime_type == 'image/jpeg':
			type = 'JPEG'
		self.filepath.seek(0)
		resize_pic = self.setPic(type)
		ret, err = qiniu.io.put(uptoken, str(self.key), resize_pic, extra)
		if err is not None:
			print 'error', err
			return
		return settings.QINIU_DOMAIN+'/'+ret['key']

	def downloadFile(self):
        """下载图片"""
        base_url = qiniu.rs.make_base_url(settings.QINIU_DOMAIN, str(self.key))
        policy = qiniu.rs.GetPolicy()
        private_url = policy.make_request(base_url)
        return private_url


    def setPic(self, type):
        """设置w*h大小图片"""
        image = Image.open(self.filepath)
        image.thumbnail((self.w, self.h), Image.ANTIALIAS)
        image_file = StringIO.StringIO()
        image.save(image_file, type, quality=90)
        image_file.seek(0)
        return image_file

    def delFile(self):
        """delete picture"""
        key = self.filepath     # 此时表示图片key 而非路径
        if key:
            ret, err = qiniu.rs.Client().delete(settings.QINIU_BUCKET_NAME, key)
            if err is not None:
                print 'error: %s ' % err
                return
        return


    def delMoreFiles(self):
        """批量删除图片"""
        remoteFile = []
        for obj in self.filepath:       # 此时filepath表示keys列表集合
            remoteFile.append(qiniu.rs.EntryPath(settings.QINIU_BUCKET_NAME, obj))
        if remoteFile:
            rets, err = qiniu.rs.Client().batch_delete(remoteFile)
            if not [ret['code'] for ret in rets] == [200, 200]:
                print 'error: %s ' % "删除失败"
                return
        return

    def getKey(self):
        """return key"""
        return self.key