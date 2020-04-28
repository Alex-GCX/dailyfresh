"""
Django settings for dailyfresh project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import sys
from django.urls import reverse

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# add by Alex 设置apps至根目录
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_wm!3sg!&9yn5@coj*jgm9pm_+cg6+leklo$3z2!)%t$4y9apx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# add by Alex 设置本地IP变量
LOCAL_IP = '192.168.183.129'

ALLOWED_HOSTS = [LOCAL_IP, ]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user', # 用户模块
    'goods', # 商品模块
    'cart', # 购物车模块
    'order', # 订单模块
    #  'tinymce', # 富文本类型
    'ckeditor', # 富文本编辑器 django-ckeditor
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dailyfresh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dailyfresh.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dailyfresh',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': LOCAL_IP,
        'PORT': 3306,
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

#################################
# add by Alex start
#################################

# 静态文件
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

#django认证系统使用的模型类
AUTH_USER_MODEL = 'user.User'
# 使用django自带的认证方法authenticate时，若用户账号密码正确，但是未激活
# 也会返回None，需要加上该设置，让其去掉激活的判断
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']

# 富文本编辑器配置
#  TINYMCE_DEFAULT_CONFIG = {
    #  'theme': 'advanced',
    #  'width': 600,
    #  'height': 400,
#  }

# 163邮箱发送
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
#发送邮件的邮箱
EMAIL_HOST_USER = 'g1242556827@163.com'
#在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = 'ENYWOVQSLWHGIUEX'
#收件人看到的发件人
EMAIL_FROM = '天天生鲜<g1242556827@163.com>'

# celery参数配置
CELERY_BROKER_URL = 'redis://localhost:6379/0' # Broker配置，使用Redis作为消息中间件
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1' # BACKEND配置，这里使用redis
CELERY_RESULT_SERIALIZER = 'json' # 结果序列化方案

# django 缓存设置cache: 使用redis数据库当做缓存的存储位置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
# django 会话设置session: 将session存储在缓存中(默认为数据表django_session中)
# 配合上面将缓存存在redis中，即可将session存在redis中
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# 用户登录地址
LOGIN_URL = '/user/login'

# 使用redis存储用户浏览记录

#################################
# add by Alex end
#################################
