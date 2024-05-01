from django.contrib import admin
from django.urls import path,include
from admin_side import views
from django.conf import settings
from django.conf.urls.static import static
from admin_side import views
from . import views

urlpatterns = [
    path('user_product_view/<int:id>',views.user_product_view,name='user_product_view'),
    
]