from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from goods.models import Goods
from django_redis import get_redis_connection

# Create your views here.
class CartView(View):
    '''购物车视图类'''
    template_name = 'cart/cart.html'
    def cart(self, request):
        '''显示购物车'''
        return render(request, self.template_name)

class CartAddView(View):
    '''加入购物车处理视图'''
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
        except Exception as e:
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
