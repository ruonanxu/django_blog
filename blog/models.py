from tkinter.constants import CASCADE

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class BlogCategory(models.Model):
    name = models.CharField(max_length=200,verbose_name='分类')  #展示字段名字

    #查询时，展示模型的字段
    def __str__(self):
        return self.name

    #管理系统中查看 模型的表名字
    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'

class Blog(models.Model):
    title = models.CharField(max_length=200,verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    pub_time = models.DateTimeField(auto_now_add=True,verbose_name='发布时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    category = models.ForeignKey(BlogCategory,on_delete=models.CASCADE,verbose_name='分类')
    author = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='作者')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '博客'
        verbose_name_plural = '博客'
        ordering = ['-pub_time']




class BlogComment(models.Model):
    comment = models.CharField(max_length=200,verbose_name='评论')
    pub_time = models.DateTimeField(auto_now_add=True,verbose_name='发布时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE,verbose_name='博客',related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name='作者')

    def __str__(self):
        return self.comment
    class Meta:
        verbose_name = '博客评论'
        verbose_name_plural = '博客评论'
        ordering = ['-pub_time']