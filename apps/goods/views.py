from django.shortcuts import render
from django.views import View

# Create your views here.

class IndexView(View):
    '''首页视图'''
    template_name = 'goods/index.html'
    def get(self, request):
        '''显示首页'''
        return render(request, self.template_name)

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
