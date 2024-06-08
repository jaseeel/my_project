from django.contrib import admin
from django.urls import path,include
from admin_side import views
from django.conf import settings
from django.conf.urls.static import static
from admin_side import views
from . import views

urlpatterns = [
    path('base',views.base,name="base"),
    path('user_product_view/<int:id>',views.user_product_view,name='user_product_view'),
    path('search/',views.product_search,name="product_search"),
    path('product_list',views.product_list,name="product_list"),
    path('sort',views.sort,name="sort"),

    
   
    
]