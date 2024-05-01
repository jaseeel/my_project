from django.contrib import admin
from django.urls import path
from .views import *
from products import views as products_views
from category import views as category_views
from inventory import views as inv_views


urlpatterns = [
    path('login/',admin_login,name='admin_login'),
    path('dashboard/',dashboard,name='dashboard'),
    path('user_management/',User_management,name='user_management'),
    path('status/<int:user_id>/block/',block,name='block_status'),
    path('status/<int:user_id>/unblock/',unblock,name='unblock_status'),
    path('<int:user_id>/delete_user',delete_user,name='delete_user'),
    path('product_management/',products_views.product_view,name='product_management'),
    path('add_product/',products_views.add_product,name='add_product'),
    path('edit_product/<int:id>/',products_views.update_product,name='edit'),
    path('block_product/<int:id>/',products_views.block_product,name='block_product'),
    path('unblock_product/<int:id>/',products_views.unblock_product,name='unblock_product'),
    path('category_management/',category_views.category_list,name='category_management'),
    path('add_category/',category_views.add_category,name='add_category'),
    path('edit_category/<int:id>/',category_views.edit_category,name='edit_category'),
    path('delete_category/<int:id>/',category_views.delete_category,name='delete_category'),
    path('block_category/<int:id>/',category_views.block_category,name='block_category'),
    path('unblock_category/<int:id>/',category_views.unblock_category,name='unblock_category'),
    path('add_brand/',category_views.add_brand,name='add_brand'),
    path('block_product/<int:id>/',products_views.block_product,name='block_product'),
    path('unblock_product/<int:id>/',products_views.unblock_product,name='unblock_product'),
    path('delete_product/<int:id>/',products_views.delete_product,name='delete_product'),
    path('logout/',admin_logout,name='admin_logout'),  
    path('banner_management/',category_views.banner_management,name='banner_management'),
    path('add_banner/',category_views.add_banner,name='add_banner'),
    path('update_banner/<int:id>',category_views.update_banner,name='update_banner'),
    path('delete_banner/<int:id>',category_views.delete_banner,name='delete_banner'),
    path('block_banner/<int:id>',category_views.block_banner,name='block_banner'),
    path('unblock_banner/<int:id>',category_views.unblock_banner,name='unblock_banner'),
    path('inventory/',inv_views.inventory,name='inventory'),
    path('update-stock/', inv_views.update_stock, name='update_stock'),
    
]