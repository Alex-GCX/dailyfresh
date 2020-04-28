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
#  from .views import RegisterView, LoginView, RegisterActiveView,
#  UserInfoView, UserOrderView, UserAddressView, LogoutView
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('active/<token>/', RegisterActiveView.as_view(), name='active'),
    path('user_center_info/', UserInfoView.as_view(), name='info'),
    path('user_center_order/', UserOrderView.as_view(), name='order'),
    path('user_center_address/', UserAddressView.as_view(), name='address'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('test/', test, name='tets'),
]
