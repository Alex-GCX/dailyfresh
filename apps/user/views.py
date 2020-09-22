import re
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django_redis import get_redis_connection
from django.core.paginator import Paginator
from utils.tasks import send_mail_task
from user.models import User, Address
from goods.models import Goods
from order.models import OrderInfo, OrderGoods

# Create your views here.

class RegisterView(View):
    '''注册视图'''
    template_name = 'user/register.html'
    content = {'errmsg': ''}

    def __init__(self):
        View.__init__(self)
        self.content = {'errmsg': ''}

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
        token = token.decode() # byte格式转为utf-7格式，默认utf-7
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

    def __init__(self):
        View.__init__(self)
        self.content['errmsg'] = ''

    def my_render(self, request, content):
        '''显示登录页面'''
        return render(request, self.template_name, content)

    def get(self, request):
        '''显示登录页面'''
        # 判断是否已登录
        if request.user.is_authenticated:
            # 已登录，跳转至首页
            return redirect(reverse('goods:index'))
        # 处理记住用户名
        # 判断cookies中是否存在用户名
        username = request.COOKIES.get('username', '')
        # 若存在，则把记住用户名的勾选框也勾上
        if username:
            checked = 'checked'
        else:
            checked = ''

        # 将cookies中的用户名和勾选框传入HTML模板
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
            return self.my_render(request, self.content)

        # 有些页面是需要用户登录后才能访问的，需要记录用户的登录状态
        login(request, user)

        # 登记登录按钮后，可能重定向到其他next网址，若无则重定向首页
        dir_url = request.GET.get('next', default=reverse('goods:index'))

        # 记住用户名
        # 先获取重定向返回的HTTPResponse对象，需要再其上面添加cookie
        response = redirect(dir_url)
        # 若记住用户名，则设置cookie，否则删除该cookie值
        if remember == 'on':
            response.set_cookie('username', username, max_age=7*24*3600)
        else:
            response.delete_cookie('username')

        return response

class LogoutView(View):
    '''登出视图'''
    def get(self, request):
        '''显示登出'''
        logout(request)
        return redirect(reverse('user:login'))

class UserInfoView(LoginRequiredMixin, View):
    '''用户中心信息类'''
    template_name = 'user/user_center_info.html'
    context = {'type': ''}

    def get(self, request):
        '''显示用户信息'''
        user = request.user
        # 获取默认收货地址
        address = Address.objects.get_default_address(user)
        self.context['type'] = 'info'
        self.context['address'] = address

        # 获取历史浏览记录
        # 连接redis数据库
        connect = get_redis_connection('default')
        # 获取当前用户key值,格式为history_userid
        history_key = 'history_%d'%(user.id)
        # 获取最新的五条历史记录
        history_list = connect.lrange(history_key, 0, 4)
        # 获取商品对象
        goods_list = [Goods.objects.get(id=i) for i in history_list]
        self.context['goods_list'] = goods_list

        return render(request, self.template_name, self.context)

class UserOrderView(LoginRequiredMixin, View):
    '''用户中心订单类'''
    template_name = 'user/user_center_order.html'
    context = {'type': ''}

    def get(self, request, page_num):
        '''显示用户订单'''
        self.context['type'] = 'order'
        user = request.user
        # 获取订单信息
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')
        # 无订单数据
        if not orders:
            self.context['page'] = None
            self.context['pages'] = None
            return render(request, self.template_name, self.context)
        # 遍历订单头
        for order in orders:
            order_goods_list = OrderGoods.objects.filter(order=order)
            # 动态给order增加属性
            order.order_goods_list = order_goods_list
            order.status_name = OrderInfo.ORDER_STATUS_DIC[order.order_status]
            order.method_name = OrderInfo.PAY_METHOD_DIC[str(order.pay_method)]
            # 遍历订单行
            for order_goods in order_goods_list:
                # 动态给order_goods增加属性
                order_goods.amount = order_goods.price * order_goods.count

        # 分页
        # 获取Paginator对象
        paginator = Paginator(orders, 2)
        total_page = paginator.num_pages
        # 校验参数页码
        if page_num > total_page:
            page_num = 1
        # 获取Page对象
        page = paginator.page(page_num)
        # 页码,页面上最多显示5页
        if total_page <=5:
            # 若总页数不超过5页
            min_page = 1
            max_page = total_page
        else:
            # 显示的最小页码
            min_page = page_num - 2
            # 显示的最大页码
            max_page = page_num + 2
            # 若最小页码小于1，则设置最小页码为1
            # 并将小于的值加在最大页码上，保证最小页码到最大页码有5页
            diff = min_page - 1
            if diff < 0:
                min_page = 1
                max_page -= diff
            # 若最大页码大于总页数，则设置最大页码为总页数
            # 并将大于的值减在最小页码上，保证最小页码到最大页码有5页
            diff = max_page - total_page
            if diff > 0:
                max_page = total_page
                min_page -= diff
        # 设置显示的页码范围
        pages = range(min_page, max_page + 1)
        # 组织上下文
        self.context['page'] = page
        self.context['pages'] = pages
        return render(request, self.template_name, self.context)

class UserAddressView(LoginRequiredMixin, View):
    '''用户中心地址类'''
    template_name = 'user/user_center_address.html'
    context = {'type': '',
               'errmsg': '',
              }
    def __init__(self):
        super().__init__()
        self.context['errmsg'] = ''

    def get(self, request):
        '''显示用户收货地址'''
        self.context['type'] = 'address'
        # 获取默认收货地址
        address = Address.objects.get_default_address(request.user)
        self.context['address'] = address
        return render(request, self.template_name, self.context)

    def post(self, request):
        '''提交默认地址'''
        # 获取当前用户，返回值类型为User.objects.get的数据库对象
        user = request.user

        # 获取数据
        receiver = request.POST['receiver']
        address = request.POST['address']
        zip_code = request.POST.get('zip_code')
        phone = request.POST['phone']

        # 校验数据必填
        if not all([receiver, address, phone]):
            self.context['errmsg'] = '数据不完整,除邮编外其他必填!'
            return render(request, self.template_name, self.context)

        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            self.context['errmsg'] = '手机格式不正确!'
            return render(request, self.template_name, self.context)

        # 数据插入数据库
        # 更新其他地址为不默认
        Address.objects.filter(user=user,
                               is_default=True).update(is_default=False,
                                                       update_time=datetime.now())
        address = user.address_set.create(user=user, receiver=receiver,
                                          address=address, zip_code=zip_code,
                                          phone=phone,
                                          is_default=True)
        return redirect(reverse('user:address'))

@login_required
def test(request):
    print(request.user)
    return HttpResponse('跳转成功')
