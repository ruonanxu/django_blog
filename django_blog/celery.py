#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : celery.py
@Time    : 2025/11/24 18:08
@Author  : alice.xu  
@Desc    : 描述信息  
"""

# proj/celery.py
import os
from celery import Celery

# 设置 Django 配置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_blog.settings')

# 初始化 Celery 应用
app = Celery('django_blog')

# 从 Django 设置中加载配置（以 CELERY_ 为前缀）
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有应用中的 tasks.py
app.autodiscover_tasks()

# 调试任务（可选）
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")