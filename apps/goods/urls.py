"""dailyfresh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import IndexView, DetailView, ListView, GoodsSearchView

urlpatterns = [
    path('goods/detail/<int:goods_id>/', DetailView.as_view(), name='detail'),
    path('goods/list/<int:goods_type_id>/<int:page_num>/', ListView.as_view(), name='list'),
    path('search/', GoodsSearchView.as_view(), name='search'),
    path('index/', IndexView.as_view(), name='index'),
]
