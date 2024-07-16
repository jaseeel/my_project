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
    path('logout_view/', views.user_logout,name='logout_view'),
    path('cancel/', views.cancel_view,name='cancel'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-otp/', views.reset_otp, name='reset_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
]