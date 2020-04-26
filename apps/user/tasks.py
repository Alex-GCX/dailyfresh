from django.conf import settings
from django.core.mail import send_mail
from dailyfresh.celery import app

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
