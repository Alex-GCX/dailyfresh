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
from .views import OrderPlaceView, OrderCreateView, OrderAlipayView
from .views import OrderCheckView, OrderCommentView

urlpatterns = [
    path('place/', OrderPlaceView.as_view(), name='place'),
    path('create/', OrderCreateView.as_view(), name='create'),
    path('alipay/', OrderAlipayView.as_view(), name='alipay'),
    path('check/', OrderCheckView.as_view(), name='check'),
    path('comment/<int:order_id>', OrderCommentView.as_view(), name='comment')
]
