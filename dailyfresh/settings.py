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
# LOCAL_IP = '192.168.183.129'
LOCAL_IP = '47.102.114.90'

ALLOWED_HOSTS = [LOCAL_IP, 'www.alex-gcx.top', 'alex-gcx.top']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #  'tinymce', # 富文本类型
    'ckeditor', # 富文本编辑器 django-ckeditor
    'haystack', # 全文搜索框架
    'sequences.apps.SequencesConfig', # django序列
    'user', # 用户模块
    'goods', # 商品模块
    'cart', # 购物车模块
    'order', # 订单模块
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
# 收集的静态文件路径
STATIC_ROOT = '/home/alex/python/dailyfresh/django_static'

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
# 阿里云发送邮件配置
EMAIL_PORT = 465
EMAIL_USE_SSL = True


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

# Fastdfs的客户端配置文件路径
FDFS_CLIENT_CONF = 'utils/fastdfs/client.conf'
# 让Django上传文件时调用自定义的文件存储类
DEFAULT_FILE_STORAGE = 'utils.fastdfs.storage.FdfsStorage'
# nginx服务器url路径
NGINX_URL = 'http://%s:8888/'%(LOCAL_IP)

# haystack+whoosh配置，全文检索框架
HAYSTACK_CONNECTIONS = {
    'default': {
        #  'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine',
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    },
}
# 设置查询结果每页显示多少条数据
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10

# 支付宝支付设置-沙箱环境
# 支付宝网关
ALIPAY_SERVER_URL = 'https://openapi.alipaydev.com/gateway.do'
# 应用ID
ALIPAY_APP_ID = '2016102200739747'
# 应用私钥
ALIPAY_PRIVATE_KEY = 'MIIEpAIBAAKCAQEAp3go2jC9b4o3+flwKtN7tnjCikipB+CbpeYcGraM8NKTfc8jP7nwzvFBJYiElm4usQ3Sh7QqDDDNPG3QuF6MHeVYBuT9ZZP9vzdPRs7R/VVRSLUCLWyZ87dMknLilkrVih9rfrwpGH35nkJO7c2zHvmNHaefOOO+Zxgv2ZCSt+ZDkuzFouZAZFEVpB/0UxlQsTKeQggqpIa6rrwCEaFwvaLl8Mboz2ErqzXdA1g29RTNB7bqTt7IfIFMgH+G1Z7tQOw+rhpmBwojs2jl/xJ8+Ai7ktBSToFqpHK3ROnYKc650vu+fLIUoXETzo9o3i15YdWCWipVEg9lpakLbdmLawIDAQABAoIBAAtMukTuoPmTs+8z+3OITYKkZ0v5Vx5m81mgSykqRBxDuRv2DATSwQLVmHW13mxgBtp/ekMZzvR/nnmDV1/5US77OJNOhCKEd8ydKMY4UkbrqM5lGD6EY2bkaVBAXDWT2xC0ygYFICi850jcZIL7LCjc4b6sfrvR8hj2stPVQ3ERBjgIPvGelgDpgGbISwozTaNJL9EpGuxSE+h8bgO3KunBM60XzaFyJoiY3afyzu+s4Gi51H6Auhkvi7quUjwyFFgYGV51nhadbNPC9SIPDOxpQaDah5Igz2PykTHLz4VDXt0PS2QU7uQQQskgnmr1KsNtR3b7icIrM5yGtg5d1lECgYEA6uhwrRrSoDKqmQBoMwRlR6a3bGXtVhyKRS3o8n0pJEwtcuwJ+OLmF32KlacZhVUjSHEsSn9w3vDXWOqpmLDs8HNDXPuPeUj64udDctVEs4neGiJ21MoOl3L3bd4ASiaAip8cx1MkG1iJ9+5aMqPWczbtns0fBomTpO6Z2J1+WAUCgYEAtoGV+Z/0ngXpkOKqGlE7DLZCDI6XaOJ4zGzGLgXe2PPTYjZwl9rk6ECxSO8mGKUqIbsdmaeHWaFWEgYHM5WRMG7sEV5PYTVYk78TOEkrv0W/S8B2pLr2CXPUJK1d9TsP4oc6D9xOsvIdA/GcK7dLsX6dnocyZiuRiHWfURZL4K8CgYEA5kqT1BC8tpKVTsPoY0OG6vSVU66lO0tlfqagfcGYKN6Jm+WtbRM8UYEg8M/NpDowCd/xdON1Swq/g4siUu/4iU3ml2yDXnregr4IELbl0EFzvRlWeAvSvETYLxx6Gjeewsd0FjD679ggAjDoukaGgZMy5wDezrDnTsUfjA3yg+UCgYAhKq+cq8sCpMRrhiWvnq+CgeTC727oqq+VRvdFCeATwUva/1W64xbSdl9Bh+R+ehWMB7s7X0yjp0RDBkFsyHOYP7A6/86hNdahEwplIjcHDZ/UHmfxS+DGmvwkpjT7Cf67BiQxGbJbptBLFS9yal8hJId0ddFc6/IIwIdxbwHfFQKBgQDJFx7UEExZRoSuzG1n9YV2TcPwUdXmih5pA9gjNr75+1zEDtzIVTyvJz0bw10hwJxUt/LsQHasOobTAZicHAzdKjDXf/dDfAvgm8YcpM1YoWHqRTPUEiI3cvYd5hii+D1Ney0ShFTD5Svq9sJtBf2H+GJmZM4IbEEZryVqNeaQeQ=='
# 支付宝公钥
ALIPAY_PUBLIC_KEY = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu7VpkMSjW6ay396lyF6LA4piwaTyJsPaedCt4Vd5gNgQP9sZA/4kZ56jh3F8a8D7/mPvzU/l8ZWQSDdh5WoF6mweGdvLLKJefdM7FY3knpxw/wZKHFJAvLbP1Myy1d7ifnkH0vy0+WyWO5bBqm1yaqIJizlBsHhMBemS5kdvApNA6nLeMANxda8wsS2O39fNTfyHNysivybbHo+jzmTZLKQHQDxyz1S9AZ0bAl/NnZxj73vgQzvqfYlWZdflxByTrjqMlAo74UGNbghsWd8vLvK75kkL3h3r6b7/KPFSJ2uAZpnFgfKk/2m5DXMD3yzLMMl+0mQFRDr3Kti3PVqddQIDAQAB'
# 订单超时时间：如果买家超过这个时间不付款,会关闭交易(最小1m分钟)
ALIPAY_EXPRESS = '10m'
# 回调通知地址
ALIPAY_NOTIFY_URL = ""
ALIPAY_RETURN_URL = ""
#################################
# add by Alex end
#################################
