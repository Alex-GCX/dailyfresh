from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from goods.models import *
from order.models import OrderGoods
from utils.utils import get_cart_count, get_index_data
from django.core.cache import cache
from django_redis import get_redis_connection
from django.core.paginator import Paginator
from haystack.generic_views import SearchView
# Create your views here.

class IndexView(View):
    '''首页视图'''
    template_name = 'goods/index.html'
    def get(self, request):
        '''显示首页'''
        # 从缓存汇总获取数据
        context = cache.get('index_data')
        if not context:
            # 获取数据库信息
            context = get_index_data()
            # 设置缓存,3600秒过期
            print('设置缓存')
            cache.set('index_data', context, 3600)

        # 获取购物车数量,购物车存储格式为：cart_userid : {'goodsid': quantity}
        cart_count = get_cart_count(request)
        context['cart_count'] = cart_count
        return render(request, self.template_name, context)

# /goods/list/goods_type_id/page_num?sort='default'
class ListView(View):
    '''商品列表视图类'''
    template_name = 'goods/list.html'

    def get(self, request, goods_type_id, page_num):
        '''显示商品列表'''
        # 获取数据信息
        # 全部商品分类
        all_type = GoodsType.objects.all()

        # 当前商品类型
        try:
            goods_type = GoodsType.objects.get(id=goods_type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 新品推荐
        new_goods = Goods.objects.filter(goodstype=goods_type).order_by('-create_time')[:2]

        # 购物车数量
        cart_count = get_cart_count(request)

        # 商品列表
        # 排序方式
        sort_dic = {
            'price': 'price',
            'hot': '-sales',
            'default': '-create_time',
        }
        # 获取url地址中的参数
        url_sort = request.GET.get('sort')
        # 将url中的排序参数与排序字典匹配，匹配不到则以默认方式
        if url_sort in sort_dic:
            sort = url_sort
        else:
            sort = 'default'
        # 获取排序字段
        order_by = sort_dic.get(sort)
        goods_list = Goods.objects.filter(goodstype=goods_type).order_by(order_by)

        # 分页
        # 创建分页对象，每页显示1条记录
        paginator = Paginator(goods_list, 1)
        # 获取总页数
        total_page = paginator.num_pages
        # 判断参数的页码是否在分页页码范围内,不在则显示第一页
        if page_num > total_page:
            page_num = 1
        # 当前页的page对象
        page = paginator.page(page_num)

        # 获取显示的页码范围，这里设置只显示三个页码
        if total_page <= 3:
            # 若总页数小于3，则将页码全部显示
            page_list = range(1, total_page+1)
        elif page_num == 1:
            # 若当前页码为1,则范围为1,2,3
            page_list = range(1, 4)
        elif page_num == total_page:
            # 若当前页码为最后一页，则将最后三个页码全部显示
            page_list = range(total_page-2, total_page+1)
        else:
            # 其他情况则显示前一页，当前页，后一页的页码
            page_list = range(page_num-1, page_num+2)

        # 组织上下文
        context = {
            'all_type': all_type,
            'goods_type': goods_type,
            'new_goods': new_goods,
            'sort': sort,
            'page': page,
            'page_list': page_list,
            'cart_count': cart_count,
        }
        return render(request, self.template_name, context)

class DetailView(View):
    '''商品详情视图类'''
    template_name = 'goods/detail.html'

    def get(self, request, goods_id):
        '''显示商品详情'''
        # 获取商品详细信息
        try:
            goods = Goods.objects.get(id=goods_id)
        except Goods.DoesNotExist:
            return redirect(reversed('goods:index'))

        # 全部商品分类
        all_type = GoodsType.objects.all()

        # 同类型下面的新品推荐
        new_goods = Goods.objects.filter(goodstype =
                                         goods.goodstype).order_by('-create_time')[:2]

        # 获取同SPU下的其他SKU
        others = Goods.objects.filter(goodsspu=goods.goodsspu).exclude(id=goods.id).order_by('sales')[:3]

        # 购物车数量
        cart_count = get_cart_count(request)

        # 获取评论
        orders = OrderGoods.objects.filter(goods=goods).exclude(comment='').order_by('-update_time')

        # 添加浏览记录
        connect = get_redis_connection('default')
        history_key = 'history_%d'%(request.user.id)
        # 删除该商品的浏览记录
        connect.lrem(history_key, 0, goods.id)
        # 添加该商品为最新浏览记录
        connect.lpush(history_key, goods.id)

        # 组织上下文
        context = {
            'goods': goods,
            'all_type': all_type,
            'new_goods': new_goods,
            'cart_count': cart_count,
            'orders': orders,
            'others': others,
        }
        return render(request, self.template_name, context)

class GoodsSearchView(SearchView):
    '''商品搜索视图'''
    def get_context_data(self, *args, **kwargs):
        context = super(GoodsSearchView, self).get_context_data(*args, **kwargs)
        # 获取想要的数据库信息
        # 获取全部商品种类
        all_type = GoodsType.objects.all()
        # 获取购物车数量
        cart_count = get_cart_count(self.request)
        # 添加上下文
        context['all_type'] = all_type
        context['cart_count'] = cart_count
        context['page'] = context['page_obj']
        print(context)
        return context
