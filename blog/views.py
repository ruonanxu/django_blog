from django.shortcuts import render,redirect, reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods,require_GET
from django.http.response import JsonResponse
from django.db.models import Q

from blog.models import BlogCategory,Blog,BlogComment
from blog.forms import BlogForm,CommentForm


# Create your views here.
@login_required()
def blog_index(request):
    blog_lists = Blog.objects.all().values('id','title','content','pub_time','author')
    context = {
        'blog_lists': blog_lists
    }
    return render(request,'index.html',context= context)

@login_required()
def blog_detail(request,detail_id):
    blog = Blog.objects.get(pk=detail_id)
    context = {
        'blog':blog
    }
    return render(request,'blog_detail.html',context= context)

@require_http_methods(['GET','POST'])
# @login_required(login_url='/auth/login/')  #等价于下面 在settings中配置 LOGIN_URL
@login_required()
def blog_public(request):
    if request.method == 'GET':
        categories = BlogCategory.objects.all()
        context = {
            'categories': categories
        }
        return render(request, 'blog_pub.html', context=context)
    else:
        form = BlogForm(request.POST)
        if not form.is_valid():
            errors = form.errors.get_json_data()
            print(errors)
            return JsonResponse({'code': 400,'message': errors})
        title = form.cleaned_data.get('title')
        content = form.cleaned_data.get('content')
        category_id = form.cleaned_data.get('category')
        Blog.objects.create(title=title,content=content,category_id=category_id,author=request.user)
        return JsonResponse({'code': 200,'message':'博客发布成功！'})


@require_http_methods(['POST'])
@login_required()
def comment_public(request,blog_id):
    form = CommentForm(request.POST)
    if not form.is_valid():
        errors = form.errors.get_json_data()
        print(errors)
        context = {
            'error':errors,
            'msg':'发布评论失败'
        }
        return render(request,'blog_detail.html',context= context)
    comment = form.cleaned_data.get('comment')
    BlogComment.objects.create(comment=comment, blog_id=blog_id,author=request.user)
    return redirect(reverse('blog:详情页',args=(blog_id,)))

@require_GET
def blog_search(request):
    key = request.GET.get('q', '').strip()
    if key:
        blogs = Blog.objects.filter(
            Q(title__icontains=key) | Q(content__icontains=key)
        ).order_by('-pub_time')
    else:
        blogs = Blog.objects.all().order_by('-pub_time')
    # 3. 传递搜索关键词到模板（用于回显和结果提示）
    return render(
        request,
        'index.html',
        context={
            'blog_lists': blogs,  # 筛选后的博客列表
            'search_key': key  # 传递搜索关键词到模板
        }
    )





