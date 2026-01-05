from django.contrib import admin

# Register your models here.

from blog.models import BlogCategory,Blog,BlogComment
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

class BlogAdmin(admin.ModelAdmin):
    list_display = ['title','content','pub_time','update_time','category','author']

class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['comment','pub_time','update_time','blog','author']

admin.site.register(BlogCategory,BlogCategoryAdmin)
admin.site.register(Blog,BlogAdmin)
admin.site.register(BlogComment,BlogCommentAdmin)