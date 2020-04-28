from django.shortcuts import render
from django.views.generic import View

# Create your views here.
class OrderView(View):
    '''订单视图类'''
    template_name = 'order/order.html'
    def get(self, request):
        '''显示订单信息'''
        return render(request, self.template_name)
