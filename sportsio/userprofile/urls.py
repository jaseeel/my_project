from django.urls import path
from userprofile import views






#User_profile Urls

urlpatterns = [
    path('', views.user_profile,name="user_profile"),
    path('add_address/', views.add_address,name="add_address")
    ]