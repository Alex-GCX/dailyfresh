from django.shortcuts import render
from django.views.generic import View

# Create your views here.
class CartView(View):
    '''购物车视图类'''
    template_name = 'cart/cart.html'
    def cart(self, request):
        '''显示购物车'''
        return render(request, self.template_name)
