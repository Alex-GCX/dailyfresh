from django.shortcuts import render
from django.views import View

# Create your views here.

class IndexView(View):
    '''首页视图'''
    template_name = 'goods/index.html'
    def get(self, request):
        '''显示首页'''
        return render(request, self.template_name)
