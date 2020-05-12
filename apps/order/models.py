from django.db import models
from db.base_model import BaseModel

# Create your models here.

class OrderInfo(BaseModel):
    '''订单模型类'''
    PAY_METHOD_DIC = {
        '1': '货到付款',
        '2': '微信支付',
        '3': '支付宝',
        '4': '银联支付',
    }
    PAY_METHOD_CHOICES = [
        (1, PAY_METHOD_DIC['1']),
        (2, PAY_METHOD_DIC['2']),
        (3, PAY_METHOD_DIC['3']),
        (4, PAY_METHOD_DIC['4']),
    ]
    ORDER_STATUS_DIC = {
        1: '待支付',
        2: '待发货',
        3: '待收货',
        4: '待评价',
        5: '已完成',
    }
    ORDER_STATUS_CHOICES = [
        (1, ORDER_STATUS_DIC[1]),
        (2, ORDER_STATUS_DIC[2]),
        (3, ORDER_STATUS_DIC[3]),
        (4, ORDER_STATUS_DIC[4]),
        (5, ORDER_STATUS_DIC[5]),
    ]

    order_num = models.CharField(max_length=30, verbose_name='订单编号')
    user = models.ForeignKey('user.User', on_delete=models.DO_NOTHING,
                            verbose_name='用户')
    address = models.ForeignKey('user.Address', on_delete=models.DO_NOTHING,
                                verbose_name='地址')
    pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES,
                                          default=3, verbose_name='支付方式')
    total_count = models.IntegerField(default=1, verbose_name='商品总数')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                      verbose_name='商品总价')
    transit_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                        verbose_name='运费')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES,
                                            default=1, verbose_name='订单状态')
    trade_no = models.CharField(max_length=128, default='', verbose_name='支付编号')

    class Meta:
        '''元数据'''
        db_table = 'df_order_info'
        verbose_name = '订单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_num

class OrderGoods(BaseModel):
    '''订单商品模型类'''
    order = models.ForeignKey('OrderInfo', on_delete=models.CASCADE, verbose_name='订单')
    goods = models.ForeignKey('goods.Goods', on_delete=models.DO_NOTHING,
                              verbose_name='商品SKU')
    count = models.IntegerField(default=1, verbose_name='商品数目')
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                verbose_name='商品价格')
    comment = models.CharField(max_length=400, default='', verbose_name='评论')

    class Meta:
        db_table = 'df_order_goods'
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name
