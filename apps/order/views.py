from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from user.models import Address
from goods.models import Goods
from order.models import OrderInfo, OrderGoods
from django_redis import get_redis_connection

# Create your views here.
class OrderPlaceView(LoginRequiredMixin, View):
    '''订单视图类'''
    template_name = 'order/order.html'
    def post(self, request):
        '''显示订单信息'''
        user = request.user
        # 获取post数据
        goods_ids = request.POST.getlist('goods_ids')
        # 校验数据
        if not goods_ids:
            return redirect(reverse('cart:cart'))
        goods_list = []
        total_count = 0
        total_amount = 0
        # redis连接
        connect = get_redis_connection('default')
        cart_key = 'cart_%d'%(user.id)
        # 获取用户要购买的商品信息
        for goods_id in goods_ids:
            try:
                goods = Goods.objects.get(id=goods_id)
                # 获取redis中的数量
                count = int(connect.hget(cart_key, goods_id))
                # 计算小计
                amount = goods.price * count
                # 给goods添加属性
                goods.count = count
                goods.amount = amount
                # 添加至goods列表
                goods_list.append(goods)
                # 汇总数量和小计
                total_amount += amount
                total_count += count
            except Goods.DoesNotExist:
                return redirect(reverse('cart:cart'), '商品不存在!')
        # 获取地址
        address_list = Address.objects.filter(user=user)
        # 运费
        transit_price = 10
        # 实付
        total_pay = transit_price + total_amount
        # 商品id字符串,以逗号隔开
        goods_str = ','.join(goods_ids)
        # 上下文
        context = {
            'goods_list': goods_list,
            'address_list': address_list,
            'total_count': total_count,
            'total_amount': total_amount,
            'transit_price': transit_price,
            'total_pay': total_pay,
            'goods_str': goods_str,
        }
        return render(request, self.template_name, context)

class OrderCreateView(View):
    '''创建订单视图'''
    def post(self, request):
        context = {
            'status': 'E',
            'errmsg': ''
        }
        user = request.user
        if not user.is_authenticated:
            context['errmsg'] = '用户未登录!'
            return JsonResponse(context)
        # 接受数据
        address_id = request.POST.get('address_id')
        pay_method = request.POST.get('pay_method')
        goods_str = request.POST.get('goods_str')

        # 校验数据
        if not all([address_id, pay_method, goods_str]):
            context['errmsg'] = '数据不完整'
            return JsonResponse(context)
        # 地址ID是否正确
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            context['errmsg'] = '地址不存在!'
            return JsonResponse(context)
        # 支付方式是否正确
        if pay_method not in OrderInfo.PAY_METHOD_DIC:
            context['errmsg'] = '支付方式不存在!'
            return JsonResponse(context)
        return redirect(reverse('user:order'))
