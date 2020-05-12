from django.conf import settings
from django.core.mail import send_mail
from dailyfresh.celery import app
from django.template import loader, RequestContext
from utils.utils import get_index_data
from goods.models import *
#  from utils.utils import get_index_context
import os

@app.task()
def send_mail_task(username, to_email, token):
    '''发送邮件任务'''
    subject = '天天生鲜激活邮件' # 邮件主题
    message = '' # 邮件内容，会被html_message覆盖
    from_email = settings.EMAIL_FROM
    recipient_list = [to_email, ]
    url = 'http://%s:8000/user/active/%s/' % (settings.LOCAL_IP, token)
    html_message = '<p1>%s,欢迎注册天天生鲜</p1></br>请点击下面链接进行激活：</br><a href=%s>%s</a>' % (username, url, url)
    send_mail(subject, message, from_email, recipient_list, html_message=html_message)

@app.task()
def generate_static_index():
    # 获取需要展示的信息
    context = get_index_data()
    context['cart_count'] = 0
    # 使用模板
    # 加载模板文件，返回模板对象
    template = loader.get_template('goods/index.html')
    # 渲染模板
    static_index = template.render(context)

    # 生成html文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index)
