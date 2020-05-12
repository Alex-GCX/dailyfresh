from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from goods.models import Goods
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class CartView(LoginRequiredMixin, View):
    '''购物车视图类'''
    template_name = 'cart/cart.html'
    def get(self, request):
        '''显示购物车'''
        user = request.user
        # 获取购物车信息
        connect = get_redis_connection('default')
        cart_key = 'cart_%d'%(user.id)
        cart = connect.hgetall(cart_key)
        # 返回给前端的goods_list
        goods_list = []
        total_count = 0
        total_amount = 0
        for goods_id, count in cart.items():
            goods = Goods.objects.get(id=int(goods_id))
            # 小计
            amount = goods.price * int(count)
            # 给goods对象新增属性
            goods.amount = amount
            goods.count = int(count)
            # 将商品添加至列表中
            goods_list.append(goods)
            # 合计
            total_count += int(count)
            total_amount += amount
        # 组织上下文
        context = {
            'goods_list': goods_list,
            'total_count': total_count,
            'total_amount': total_amount,
        }
        return render(request, self.template_name, context)

class CartAddView(View):
    '''加入购物车处理视图'''
    def post(self, request):
        '''加入购物车处理'''
        user = request.user
        context = {
            'status': 'E',
            'errmsg': ''
        }
        # 判断是否登录
        if not user.is_authenticated:
            context['errmsg'] = '用户未登录!'
            return JsonResponse(context)

        # 接收数据
        goods_id = request.POST.get('goods_id')
        count = request.POST.get('count')

        # 校验数据
        # 数据是否完整
        if not all([goods_id, count]):
            context['errmsg'] = '数据不完整!'
            return JsonResponse(context)
        # 商品是否存在
        try:
            goods_id = int(goods_id)
            goods = Goods.objects.get(id=goods_id)
        except Goods.DoesNotExist:
            context['errmsg'] = '用户未登录!'
            return JsonResponse(context)
        # 数量格式是否正确
        try:
            count = int(count)
        except Exception as e:
            context['errmsg'] = '商品数量格式不正确!'
            return JsonResponse(context)

        # 逻辑处理：添加购物车
        # 连接redis
        connect = get_redis_connection('default')
        cart = 'cart_%d'%(user.id)
        # 获取原购物车中goods_id的数量
        old_count = connect.hget(cart, goods_id)
        if old_count:
            count += int(old_count)
        # 判断是否超过库存
        if count > goods.onhand:
            context['errmsg'] = '超出库存数量!'
            return JsonResponse(context)
        # 将新数量保存至数据库
        connect.hset(cart, goods_id, count)
        # 获取新购物车数量
        cart_count = connect.hlen(cart)

        # 返回数据
        context['status'] = 'S'
        context['cart_count'] = cart_count
        return JsonResponse(context)

class CartChangeView(View):
    '''购物车改变视图'''
    def post(self, request):
        user = request.user
        context = {
            'status': 'E',
            'errmsg': ''
        }
        # 判断是否登录
        if not user.is_authenticated:
            context['errmsg'] = '用户未登录!'
            return JsonResponse(context)

        # 获取数据
        goods_id = request.POST.get('goods_id')
        count = request.POST.get('count')

        # 校验数据
        if not all([goods_id, count]):
            context['errmsg'] = '数据不完整!'
            return JsonResponse(context)
        # 商品是否存在
        try:
            goods = Goods.objects.get(id=int(goods_id))
        except Goods.DoesNotExist:
            context['errmsg'] = '商品不存在!'
            return JsonResponse(context)
        # 数量格式是否正确
        try:
            count = int(count)
        except Exception as e:
            context['errmsg'] = '数量格式不正确!'
            return JsonResponse(context)

        # 更新redis数据库
        connect = get_redis_connection('default')
        cart_key = 'cart_%d'%(user.id)
        # 校验库存
        if count > goods.onhand:
            context['errmsg'] = '库存不足!'
            # 返回原数量
            context['count'] = int(connect.hget(cart_key, goods_id))
            return JsonResponse(context)

        # 更新值
        connect.hset(cart_key, goods_id, count)

        # 重新计算总件数
        total_count = 0
        values = connect.hvals(cart_key)
        for val in values:
            total_count += int(val)
        # 上下文
        context['amount'] = goods.price * count
        context['total_count'] = total_count
        context['status'] = 'S'
        return JsonResponse(context)

class CartDeleteView(View):
    '''购物车删除视图'''
    def post(self, request):
        user = request.user
        context = {
            'status': 'E',
            'errmsg': ''
        }
        if not user.is_authenticated:
            context['errmsg'] = '用户未登录!'
            return JsonResponse(context)
        # 接收数据
        goods_id = request.POST.get('goods_id')

        # 校验数据
        try:
            goods_id = int(goods_id)
            goods = Goods.objects.get(id=goods_id)
        except Exception as e:
            context['errmsg'] = '商品不存在'
            return JsonResponse(context)

        # 删除购物车数据
        connect = get_redis_connection('default')
        cart_key = 'cart_%d'%(user.id)
        connect.hdel(cart_key, goods_id)

        # 重新获取商品数量
        vals = connect.hvals(cart_key)
        total_count = 0
        for val in vals:
            total_count += int(val)

        # 上下文
        context['total_count'] = total_count
        context['status'] = 'S'
        return JsonResponse(context)
