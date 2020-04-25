from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.contrib.auth import authenticate
from .models import User
import re

# Create your views here.

class RegisterView(View):
    '''注册视图'''
    template_name = 'user/register.html'

    def my_render(self, request, errmsg=''):
        '''显示注册页面'''
        return render(request, self.template_name, {'errmsg': errmsg})

    def get(self, request):
        '''显示注册页面'''
        return self.my_render(request)

    def post(self, request):
        '''提交表单'''
        # 1.获取数据
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
        allow = request.POST.get('allow', 'off')

        # 2.校验数据

        # 2.0 判断是否勾选同意协议
        if allow != 'on':
            return self.my_render(request, '请同意协议!')

        # 2.1 判断必输
        if not all([username, password, cpwd, email]):
            return self.my_render(request, '信息未填写完整!')

        # 2.2 判断用户名是否已存在
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            return self.my_render(request, '该用户已存在!')

        # 2.3 判断两次密码是否相同
        if password != cpwd:
            return self.my_render(request, '两次密码不一致!')

        # 2.4 判断邮箱格式
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9]+(\.[a-z]{2,5}){1,2}$',
                        email):
            return self.my_render(request, '邮箱格式不正确!')

        # 3.处理注册逻辑
        user = User.objects.create_user(username, email, password)
        user.is_activate = 0
        user.save()

        return redirect(reverse('user:login'))

class LoginView(View):
    '''登录视图'''
    template_name = 'user/login.html'

    def get(self, request):
        '''显示登录页面'''
        return render(request, self.template_name)
