"""blog_c1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve

from app_all import views
from app_all import urls as app_all_urls
urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'login/', views.login),
    path(r'logout/', views.logout),
    path(r'reg/', views.register),
    path(r'index/', views.index),
    
    # 将所有以blog开头的url都交给app下面的urls.py来处理
    url(r'^blog/', include(app_all_urls)),
    
    # 极验滑动验证码 获取验证码的url
    path(r'pc-geetest/register', views.get_geetest),
    # 专门用来校验用户名是否已被注册的接口
    path(r'check_username_exist/', views.check_username_exist),
    # media相关的路由设置
    url(r'^media/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}),
]
