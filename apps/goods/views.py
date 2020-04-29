from django.shortcuts import render
from django.views import View
from goods.models import *

# Create your views here.

class IndexView(View):
    '''首页视图'''
    template_name = 'goods/index.html'
    def get(self, request):
        '''显示首页'''
        # 获取数据库信息
        # 获取商品分类
        goods_type = GoodsType.objects.all()

        # 获取轮播商品
        goods_banner = IndexGoodsBanner.objects.all()

        # 获取活动信息
        promotion_banner = IndexPromotionBanner.objects.all()

        # 获取分类商品展示信息
        for goodstype in goods_type:
            # 获取该类型下面的商品的标题信息
            title_banner = IndexTypeGoodsBanner.objects.filter(goodstype=goodstype,
                                                               display_type=0).order_by('index')
            # 获取该类型下面的商品的图片信息
            image_banner = IndexTypeGoodsBanner.objects.filter(goodstype=goodstype,
                                                               display_type=1).order_by('index')
            # 动态给type增加属性，分别保存首页分类商品的文字信息和图片信息
            goodstype.title_banner = title_banner
            goodstype.image_banner = image_banner
        # 上下文
        context = {
            'goods_type': goods_type,
            'goods_banner': goods_banner,
            'promotion_banner': promotion_banner,
        }
        return render(request, self.template_name, context)

class LisetView(View):
    '''商品列表视图类'''
    template_name = 'goods/list.html'

    def get(self, request):
        '''显示商品列表'''
        return render(request, self.template_name)

class DetailView(View):
    '''商品详情视图类'''
    template_name = 'good/detail.html'

    def get(self, request):
        '''显示商品详情'''
        return render(request, self.template_name)
