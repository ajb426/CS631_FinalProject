"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from myapp.views import register, add_to_cart, view_cart, checkout_view, remove_item_from_cart, product_detail, profile, ajax_load_address, ajax_load_paymentDetail
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from customadmin.views import admin


urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', register, name='register'),
    path('', include('myapp.urls')),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove_item_from_cart/<int:product_id>/', remove_item_from_cart, name='remove_item_from_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('checkout/', checkout_view, name='checkout_view'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('profile/', profile, name='profile'),
    path('ajax/load-address/', ajax_load_address, name='ajax_load_address'),
    path('ajax/load-paymentDetail/', ajax_load_paymentDetail, name='ajax_load_paymentDetail'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('/customadmin/', admin, name='custom_admin'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)