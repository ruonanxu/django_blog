from django.shortcuts import render,redirect,reverse
from django.http.response import JsonResponse
import random,string
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model,login,logout
from django.contrib.auth.decorators import login_required


from auth_new.models import CaptchaModel
from auth_new.forms import LoginForm, RegisterForm
from .tasks import send_async_email

User = get_user_model()


def send_email_captcha(request):
    # ?email=xxx
    email = request.GET.get('email')
    if not email:
        return JsonResponse({'code':400,'message':'必须传递邮箱'})
    #生成验证码 (4位阿拉伯数字)
    captcha = ''.join(random.sample(string.digits,4))
    print(captcha)
    CaptchaModel.objects.update_or_create(email=email,defaults={'captcha':captcha})
    task = send_async_email.delay(
        subject="Hello Celery，博客注册验证码",
        message=f"这是一封异步发送的邮件，您注册的验证码是：{captcha}",
        recipient=email
    )
    # send_mail('博客注册验证码',message=f'您注册的验证码是：{captcha}',from_email=None,recipient_list=[email])
    return JsonResponse({'code':200,'message':f'邮件已进入异步队列，即将发送,验证码是{captcha}','task_id': task.id,})


@require_http_methods(['GET','POST'])
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if not form.is_valid():
            errors= form.errors.get_json_data()
            print(errors)
            return render(request, 'register.html', {'error': errors})
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        email = form.cleaned_data.get('email')
        User.objects.create_user(username=username,password=password,email=email)
        return redirect(reverse('auth_new:login'))
    else:
        return render(request, 'register.html',{'error': ''})



@require_http_methods(['GET','POST'])
def login_action(request):
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        form = LoginForm(request.POST)
        if not form.is_valid():
            errors= form.errors.get_json_data()
            print(errors)
            return render(request, 'login.html', {'error': errors})
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        remember = form.cleaned_data.get('remember')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            login(request,user)
            if not remember:
                request.session.set_expiry(0)
            return redirect(reverse('blog:首页'))
        else:
            print('邮箱或密码错误')
            form.add_error('email','邮箱或密码错误')
            errors = form.errors.get_json_data()
            return render(request, 'login.html', {'error': errors})

@login_required()
def logout_action(request):
    logout(request)
    return redirect(reverse('blog:首页'))



