from django.urls import path
from blog import views

app_name = 'blog'

urlpatterns = [
    path('index/',views.blog_index,name='首页'),
    path('detail/<int:detail_id>',views.blog_detail,name='详情页'),
    path('public/',views.blog_public,name='发布页'),
    path('public/comment/<int:blog_id>',views.comment_public,name='发布评论'),
    path('search/',views.blog_search,name='搜索'),
]