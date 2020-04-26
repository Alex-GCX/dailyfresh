from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 为celery设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')

# 创建应用
app = Celery("dailyfresh")

#使用CELERY_ 作为前缀，在settings中写配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 设置从已经安装的app中自动加载任务
app.autodiscover_tasks()
