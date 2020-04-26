import re
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from .tasks import send_mail_task
from .models import User

# Create your views here.

class RegisterView(View):
    '''注册视图'''
    template_name = 'user/register.html'
    content = {'errmsg': ''}

    def my_render(self, request, content):
        '''显示注册页面'''
        return render(request, self.template_name, content)

    def get(self, request):
        '''显示注册页面'''
        return self.my_render(request, self.content)

    def post(self, request):
        '''提交表单'''

        '''
        1.获取数据
        '''
        username = request.POST['username']
        password = request.POST['pwd']
        email = request.POST['email']
        cpwd = request.POST['cpwd']
        # allow = request.POST['allow']
        '''
        直接调用POST方法方法时，返回的是一个dic
        当key值不存在时,会抛出异常 MultiValueDictKeyError
        这里的allow前端对应的是checkbox,当不勾选时,value值为空,则POST返回的
        字典中不会存在key为allow的值,所以为了避免异常,使用字典的get('key',default=)
        '''
        allow = request.POST.get('allow', default='off')

        '''
        2.校验数据
        '''
        # 2.0 判断是否勾选同意协议
        if allow != 'on':
            self.content['errmsg'] = '请同意协议!'
            return self.my_render(request, self.content)

        # 2.1 判断必输
        if not all([username, password, cpwd, email]):
            self.content['errmsg'] = '信息未填写完整!'
            return self.my_render(request, self.content)

        # 2.2 判断用户名是否已存在
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            self.content['errmsg'] = '该用户已存在!'
            return self.my_render(request, self.content)

        # 2.3 判断两次密码是否相同
        if password != cpwd:
            self.content['errmsg'] = '两次密码不一致!'
            return self.my_render(request, self.content)

        # 2.4 判断邮箱格式
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9]+(\.[a-z]{2,5}){1,2}$',
                        email):
            self.content['errmsg'] = '邮箱格式不正确!'
            return self.my_render(request, self.content)

        '''
        3.处理注册逻辑
        '''

        # 3.1 创建用户
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 3.2 发送激活邮件
        # 通过itsdangerous加密user_id
        # 创建加密对象,3600秒后过期
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'userid': user.id} # 定义加密信息
        token = serializer.dumps(info) # 进行加密
        token = token.decode() # byte格式转为utf-8格式，默认utf-8
        send_mail_task.delay(username, email, token)

        return redirect(reverse('user:login'))

class RegisterActiveView(View):
    '''注册激活视图'''
    def get(self, request, token):
        # 解密token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取userid
            user_id = info['userid']
            # 更新数据库数据
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 返回登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired:
            # 链接已过期
            return HttpResponse('激活链接已过期！')

class LoginView(View):
    '''登录视图'''
    template_name = 'user/login.html'
    content = {'errmsg': ''}

    def my_render(self, request, content):
        '''显示登录页面'''
        return render(request, self.template_name, content)

    def get(self, request):
        '''显示登录页面'''
        # 处理记住用户名
        username = request.COOKIES.get('username', '')
        if username:
            checked = 'checked'
        else:
            checked = ''
        self.content['username'] = username
        self.content['checked'] = checked
        return self.my_render(request, self.content)

    def post(self, request):
        '''
        获取数据
        '''
        username = request.POST['username']
        password = request.POST['password']
        remember = request.POST.get('remember', 'off')
        '''
        校验数据
        '''
        user = authenticate(username=username, password=password)
        if not user:
            self.content['errmsg'] = '用户名或密码不正确!'
            return self.my_render(request, self.content)

        # 判断是否激活
        if user.is_active == 0:
            self.content['errmsg'] = '用户未激活!'

        # 有些页面是需要用户登录后才能访问的，需要记录用户的登录状态
        login(request, user)

        # 记住用户名
        response = redirect(reverse('goods:index'))
        print('---------------------')
        print(remember)
        print(username)
        if remember == 'on':
            print(username)
            response.set_cookie('username', username, max_age=7*24*3600)
        else:
            response.delete_cookie('username')

        return response
