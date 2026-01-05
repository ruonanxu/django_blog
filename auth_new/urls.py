from django.urls import path
from auth_new import views

app_name = 'auth_new'
urlpatterns = [
    path('login/',views.login_action,name='login'),
    path('logout/',views.logout_action,name='logout'),
    path('register/',views.register,name='register'),
    path('captcha/',views.send_email_captcha,name='发送邮箱验证码')
]