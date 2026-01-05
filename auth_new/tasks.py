#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : tasks.py
@Time    : 2025/11/24 18:18
@Author  : alice.xu  
@Desc    : 描述信息  
"""
# app/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from celery.signals import task_success
import requests
import json

# --------------------------
# 配置项：替换为你的钉钉 Webhook
# --------------------------

DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=06294948e3d340fa5354c8c7c9f0a1e22b775bd3649b643a8866d56f1871c625"
DINGTALK_KEYWORD = "ad"  # 钉钉机器人设置的自定义关键词


@shared_task(bind=True, max_retries=2)
def send_dingtalk_msg(self, title, content):
    """异步发送钉钉消息（支持文本/Markdown 格式）"""
    try:
        # 钉钉消息格式（Markdown 更美观，支持换行、加粗）
        msg_body = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": f"### {title}\n\n{content}\n\n"
            }
        }

        # 发送 HTTP 请求到钉钉 Webhook
        response = requests.post(
            url=DINGTALK_WEBHOOK,
            headers={"Content-Type": "application/json"},
            data=json.dumps(msg_body),
            timeout=10
        )

        # 校验响应结果
        result = response.json()
        if result.get("errcode") != 0:
            raise Exception(f"钉钉消息发送失败：{result.get('errmsg')}")

        print(f"钉钉消息已发送：{title}")
        return f"钉钉消息发送成功：{title}"

    except Exception as exc:
        # 钉钉消息发送失败，重试 2 次
        self.retry(exc=exc, countdown=5)


@shared_task(bind=True, max_retries=3)
def send_async_email(self, subject, message, recipient):
    """异步发邮件，成功后触发钉钉消息"""
    try:
        # 1. 执行发邮件逻辑
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        email_result = f"邮件已成功发送至 {recipient}，主题：{subject}"
        print(email_result)

        # 2. 邮件成功后，触发钉钉消息任务（串行调用）
        # 方式 1：直接调用钉钉任务（简单，任务串行执行）
        # send_dingtalk_msg.delay(
        #     title=f"【{DINGTALK_KEYWORD}】邮件发送成功",
        #     content=email_result
        # )

        # 方式 2：使用 Celery 回调（更灵活，支持链式任务）
        # send_async_email.s(subject, message, recipient).then(send_dingtalk_msg.s(title, content))
        # （需结合 chain 机制，适合复杂任务流）

        return email_result

    except Exception as exc:
        # 邮件发送失败，重试（不触发钉钉消息）
        self.retry(exc=exc, countdown=3 ** self.request.retries)



@task_success.connect(sender=send_async_email)  # 仅监听 send_async_email 任务成功事件
def trigger_dingtalk_after_email_success(sender, result, **kwargs):
    """邮件任务成功后，通过信号触发钉钉消息"""
    # result 是 send_async_email 的返回值（如 "邮件已成功发送至 xxx"）
    send_dingtalk_msg.delay(
        title=f"【{DINGTALK_KEYWORD}】邮件发送成功",
        content=result
    )