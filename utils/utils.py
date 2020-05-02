from django_redis import get_redis_connection
from goods.models import *

def get_cart_count(request):
    '''获取用户购物车数量'''
    # 获取购物车数据,购物车存储格式为：cart_userid : {'goodsid': quantity}
    # 初始化购物车数量
    cart_count = 0
    # 判断是否登录
    user = request.user
    if user.is_authenticated:
        # 连接redis数据库
        connect = get_redis_connection('default')
        # 构造key
        cart_key = 'cart_%d'%(user.id)
        # 获取hash中元素的个数
        cart_count = connect.hlen(cart_key)
    return cart_count

def get_index_data():
    '''获取首页数据信息'''
    # 获取商品分类
    goods_type = GoodsType.objects.all()
    # 获取轮播商品
    goods_banner = IndexGoodsBanner.objects.all().order_by('index')
    # 获取活动信息
    promotion_banner = IndexPromotionBanner.objects.all().order_by('index')

    # 获取分类商品展示信息
    for goodstype in goods_type:
        # 获取该类型下面的商品的标题信息,并进行排序
        title_banner = IndexTypeGoodsBanner.objects.filter(goodstype=goodstype,
                                                           display_type=0).order_by('index')
        # 获取该类型下面的商品的图片信息,并进行排序
        image_banner = IndexTypeGoodsBanner.objects.filter(goodstype=goodstype,
                                                           display_type=1).order_by('index')
        # 动态给type增加属性，分别保存首页分类商品的文字信息和图片信息
        goodstype.title_banner = title_banner
        goodstype.image_banner = image_banner

    # 组织上下文
    context = {
        'goods_type': goods_type,
        'goods_banner': goods_banner,
        'promotion_banner': promotion_banner,
    }
    return context
