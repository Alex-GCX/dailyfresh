from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django_redis import get_redis_connection
from django.conf import settings
from sequences import get_next_value
from datetime import datetime
import time
import traceback
from user.models import Address
from goods.models import Goods
from order.models import OrderInfo, OrderGoods
# 支付宝支付 start
import logging
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
# 支付宝支付 end

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
                try:
                    count = int(connect.hget(cart_key, goods_id))
                except Exception as e:
                    return redirect(reverse('cart:cart'))
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
                return redirect(reverse('cart:cart'))
        # 获取地址
        address_list = Address.objects.filter(user=user)
        # 运费
        transit_amount = 10
        # 实付
        total_pay = transit_amount + total_amount
        # 商品id字符串,以逗号隔开
        goods_str = ','.join(goods_ids)
        # 上下文
        context = {
            'goods_list': goods_list,
            'address_list': address_list,
            'total_count': total_count,
            'total_amount': total_amount,
            'transit_amount': transit_amount,
            'total_pay': total_pay,
            'goods_str': goods_str,
        }
        return render(request, self.template_name, context)

class OrderCreateView(View):
    '''创建订单视图'''
    @transaction.atomic
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
            address_id = int(address_id)
            address = Address.objects.get(id=address_id)
        except Exception as e:
            context['errmsg'] = '地址不存在!'
            return JsonResponse(context)
        # 支付方式是否正确
        if pay_method not in OrderInfo.PAY_METHOD_DIC:
            context['errmsg'] = '支付方式不存在!'
            return JsonResponse(context)
        pay_method = int(pay_method)

        # 创建订单
        # 订单头信息
        # 使用日期+序列创建订单号
        order_sequence = get_next_value('order')
        order_num = datetime.now().strftime('%Y%m%d%H%M%S')+str(order_sequence)
        total_count = 0
        total_amount = 0
        transit_amount = 10
        # 设置保存点
        save_id = transaction.savepoint()
        try:
            # 创建订单头记录
            order = OrderInfo.objects.create(order_num=order_num,
                                             user=user,
                                             address=address,
                                             pay_method=pay_method,
                                             total_count=total_count,
                                             total_amount=total_amount,
                                             transit_amount=transit_amount)
            # 连接redis
            connect = get_redis_connection('default')
            cart_key = 'cart_%d'%(user.id)
            # 创建订单行记录
            goods_ids = goods_str.split(',')
            for goods_id in goods_ids:
                for i in range(1, 4):
                    try:
                        goods = Goods.objects.get(id=goods_id)
                        # 悲观锁
                        # goods = Goods.objects.select_for_update().get(id=goods_id)
                    except Goods.DoesNotExist:
                        transaction.savepoint_rollback(save_id)
                        context['errmsg'] = '商品不存在!'
                        return JsonResponse(context)
                    #  print('username:%s onhand:%d'%(user.username, goods.onhand))
                    #  import time
                    #  time.sleep(5)
                    # 获取数量
                    try:
                        count = int(connect.hget(cart_key, goods_id))
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        context['errmsg'] = '购物车中不存在提交的商品!'
                        return JsonResponse(context)
                    # 校验是否超库存
                    old_onhand = goods.onhand
                    if count > old_onhand:
                        transaction.savepoint_rollback(save_id)
                        context['errmsg'] = '库存不足!'
                        return JsonResponse(context)

                    # 计算新库存和新销量
                    new_onhand = old_onhand - count
                    new_sales = goods.sales + count

                    # 乐观锁，更新goods start
                    affected_rows = Goods.objects.filter(id=goods_id,
                                                         onhand=old_onhand).update(onhand=new_onhand,
                                                                                   sales=new_sales)
                    # 若受影响条数为0，即没有更新goods,则继续尝试
                    if affected_rows == 0:
                        if i == 3:
                            #第三次尝试还是没更新到数据,则认为失败
                            transaction.savepoint_rollback(save_id)
                            context['errmsg'] = '下单失败'
                        continue
                    # 乐观锁 end
                    # 创建订单行信息
                    OrderGoods.objects.create(goods=goods,
                                              order=order,
                                              count=count,
                                              price=goods.price)
                    # 获取小计
                    amount = goods.price * count
                    # 汇总数量和价格
                    total_count += count
                    total_amount += amount
                    # 更新商品表的销量和库存
                    #  goods.onhand = new_onhand
                    #  goods.sales = new_sales
                    #  goods.save()
                    break
            # 更新订单头总数量和总价格
            order.total_amount = total_amount
            order.total_count = total_count
            order.save()
            # 删除购物车
            connect.hdel(cart_key, *goods_ids)
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            context['errmsg'] = '创建订单失败!'
        # 返回应答
        transaction.savepoint_commit(save_id)
        context['status'] = 'S'
        return JsonResponse(context)

def alipay_init():
    '''支付宝初始化'''
    # 记录日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        filemode='a',)
    logger = logging.getLogger('')
    # 实例化客户端
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = settings.ALIPAY_SERVER_URL
    alipay_client_config.app_id = settings.ALIPAY_APP_ID
    alipay_client_config.app_private_key = settings.ALIPAY_PRIVATE_KEY
    alipay_client_config.alipay_public_key = settings.ALIPAY_PUBLIC_KEY
    client = DefaultAlipayClient(alipay_client_config, logger)
    return client

def alipay_pay(order):
    '''支付宝支付'''
    client = alipay_init()
    # 构造请求参数对象
    model = AlipayTradePagePayModel()
    model.out_trade_no = order.order_num;
    model.total_amount = str(order.total_amount);
    model.subject = "天天生鲜";
    model.timeout_express = settings.ALIPAY_EXPRESS
    #与支付宝签约的产品码名称，目前只支持这一种。
    model.product_code = 'FAST_INSTANT_TRADE_PAY'
    request = AlipayTradePagePayRequest(biz_model=model)
    #  request.return_url = settings.ALIPAY_RETURN_URL
    request.notify_url = settings.ALIPAY_NOTIFY_URL

    # 执行API调用,获取支付连接
    pay_url = client.page_execute(request, http_method='GET')
    return pay_url

def alipay_query(order, context):
    '''支付宝支付'''
    client = alipay_init()
    # 构造请求参数对象
    model = AlipayTradeQueryModel()
    model.out_trade_no = order.order_num;
    model.timeout_express = settings.ALIPAY_EXPRESS
    #与支付宝签约的产品码名称，目前只支持这一种。
    model.product_code = 'FAST_INSTANT_TRADE_PAY'
    request = AlipayTradeQueryRequest(biz_model=model)

    while True:
        # 执行API调用
        response = client.execute(request)
        # str转换为字典
        response = eval(response)
        code = response.get('code')
        sub_code = response.get('sub_code')
        sub_msg = response.get('sub_msg')
        trade_status = response.get('trade_status')
        if sub_code == 'ACQ.TRADE_NOT_EXIST' or (code == '10000' and
                                                 trade_status ==
                                                 'WAIT_BUYER_PAY'):
            # 交易不存在，则继续等待用户付款
            time.sleep(5)
            continue
        elif code == '10000' and trade_status == 'TRADE_SUCCESS':
            # 支付成功
            context['status'] = 'S'
            trade_no = response.get('trade_no')
            # 回写订单支付号
            order.trade_no = trade_no
            order.order_status = 4 # 待评价
            order.save()
            break
        else:
            context['errmsg'] = '支付失败:%s-%s' % (sub_code, sub_msg)
            break

class OrderAlipayView(View):
    '''支付视图'''
    def post(self, request):
        '''支付处理'''
        context = {
            'status': 'E',
            'errmsg': '',
        }
        user = request.user
        if not user.is_authenticated:
            context['errmsg'] = '用户未登录!'
            return JsonResponse(context)
        # 接收数据
        order_id = int(request.POST.get('order_id'))

        # 校验数据
        try:
            order = OrderInfo.objects.get(id=order_id)
        except OrderInfo.DoesNotExist:
            context['errmsg'] = '订单不存在!'
            return JsonResponse(context)

        # 业务处理
        pay_url = alipay_pay(order)

        # 返回应答
        context['status'] = 'S'
        context['pay_url'] = pay_url
        return JsonResponse(context)

class OrderCheckView(View):
    '''查询支付宝支付情况'''
    def post(self, request):
        context = {
            'status': 'E',
            'errmsg': ''
        }
        user = request.user
        if not user.is_authenticated:
            context['errmsg'] = '用户未登录!'
            return JsonResponse(context)
        # 接收数据
        order_id = int(request.POST.get('order_id'))
        try:
            order = OrderInfo.objects.get(id=order_id)
        except Exception as e:
            context['errmsg'] = '订单不存在!'
            return JsonResponse(context)

        # 执行查询
        alipay_query(order, context)
        return JsonResponse(context)

class OrderCommentView(LoginRequiredMixin, View):
    '''订单评价视图'''
    template_name = 'order/order_comment.html'
    def get(self, request, order_id):
        '''显示评价页面'''
        user = request.user
        # 校验数据
        if not order_id:
            return redirect(reverse('user:order'))
        try:
            order = OrderInfo.objects.get(id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse('user:order'))
        # 获取订单商品
        order_goods_list = OrderGoods.objects.filter(order=order)
        for order_goods in order_goods_list:
            order_goods.amount = order_goods.count * order_goods.price
        # 动态赋值属性
        order.status_name = OrderInfo.ORDER_STATUS_DIC[order.order_status]
        order.order_goods_list = order_goods_list
        return render(request, self.template_name, {'order': order})

    def post(self, request, order_id):
        '''评价提交'''
        user = request.user
        # 获取数据
        total_count = int(request.POST.get('total_count'))
        # 校验数据
        if not order_id:
            return redirect(reverse('user:order', kwargs={'page_num': 1}))
        try:
            order = OrderInfo.objects.get(id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            redirect(reverse('user:order', kwargs={'page_num': 1}))

        for i in range(1, total_count+1):
            # 获取评论
            comment = request.POST.get('content_%d' % i, '')
            # 获取商品ID
            goods_id = int(request.POST.get('goods_%d' % i))
            try:
                goods = OrderGoods.objects.get(order=order, goods_id=goods_id)
            except Goods.DoesNotExist:
                continue
            goods.comment = comment
            goods.save()

        order.order_status = 5  # 已完成
        order.save()

        return redirect(reverse('user:order', kwargs={'page_num': 1}))
