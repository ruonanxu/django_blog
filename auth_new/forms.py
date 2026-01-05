from django import forms
import re
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from auth_new.models import CaptchaModel

User = get_user_model()

def validate_password_complexity(value):
    # 规则：至少8位，包含大小写字母、数字、特殊符号（任选三种）
    if len(value) < 8:
        raise ValidationError("密码长度至少8位")
    # 检查是否包含大小写字母、数字、特殊符号
    patterns = [
        r'[A-Z]',  # 大写字母
        r'[a-z]',  # 小写字母
        r'\d',  # 数字
        r'[^A-Za-z0-9]'  # 特殊符号
    ]
    matches = sum(1 for p in patterns if re.search(p, value))
    if matches < 3:
        raise ValidationError("密码需包含大小写字母、数字、特殊符号中的至少三种")


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=16,
        min_length=2,
        error_messages={
        'min_length':'输入最小长度不能小于2',
        'max_length':'输入最大长度不能大于16'
        },
        required=True,
        label= '用户名')
    email = forms.EmailField(
        error_messages={
        'required':'请输入邮箱',
        'invalid':'请输入正确的邮箱格式'
        },
        required=True,
        label= '邮箱')
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput,
        validators=[validate_password_complexity],  # 应用自定义验证器
        required=True,
    )
    # password2 = forms.CharField(
    #     label="确认密码",
    #     widget=forms.PasswordInput,
    #     validators=[validate_password_complexity],  # 应用自定义验证器
    #     required=True,
    # )
    captcha = forms.CharField(
        label="验证码",
        required=True,
        max_length=4,
        min_length=4,
        error_messages={
            'min_length': '验证码只能是4位',
            'max_length': '验证码只能是4位'
        },
    )

    # def clean_captcha(self):
    #     #若email验证失败，会导致email=None，因为 若email验证成功后，才会把 email 存入 cleaned_data中，故将其 挪到 clean 中
    #     captcha = self.cleaned_data.get('captcha')
    #     email = self.cleaned_data.get('email')
    #     print(email)
    #     email_captcha = CaptchaModel.objects.filter(email=email,captcha=captcha)
    #     print(email_captcha.query)
    #     if not email_captcha:
    #         raise ValidationError('邮箱与输入验证码匹配关系 在数据库中不存在')
    #     return  captcha

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = User.objects.filter(email=email).exists()
        if user:
            raise ValidationError('该用户已存在')
        return email


    #重写 clean 方法，校验 2次输入的密码是否一致
    def clean(self):
    #     cleaned_data = super().clean()
    #     pwd1 = cleaned_data.get('password1')
    #     pwd2 = cleaned_data.get('password2')
    #     if pwd1!= pwd2:
    #         raise ValidationError('2次输入的密码值不一致')
        #所有字段都验证好了，才会执行clean
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        captcha = cleaned_data.get('captcha')

        # 只有 email 和 captcha 都通过验证时，才校验匹配关系
        if email and captcha:
            exists = CaptchaModel.objects.filter(email=email, captcha=captcha).exists()
            if not exists:
                # 用 add_error 绑定错误到 captcha 字段，前端能正确显示
                self.add_error('captcha', '验证码错误或与邮箱不匹配')
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        error_messages={
        'required':'请输入邮箱',
        'invalid':'请输入正确的邮箱格式'
        },
        required=True,
        label= '邮箱')
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput,
        validators=[validate_password_complexity],  # 应用自定义验证器
        required=True,
    )
    remember = forms.IntegerField(required=False)
