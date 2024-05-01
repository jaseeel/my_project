from django.contrib import admin
from django.urls import path,include
from admin_side import views
from django.conf import settings
from django.conf.urls.static import static
from admin_side import views
from registration import views
urlpatterns = [
    path('login/', views.user_login,name='login'),
    path('register/', views.register,name='register'),
    path('forget/',views.forget,name='forget'),
    path('otp/', views.verify_otp,name='otp'),
    path('logout_view/', views.logout_view,name='logout_view'),
    path('cancel/', views.cancel_view,name='cancel'),
]