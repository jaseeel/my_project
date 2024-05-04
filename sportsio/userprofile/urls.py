from django.urls import path
from userprofile import views






#User_profile Urls

urlpatterns = [
    path('', views.user_profile,name="user_profile"),
    path('add_address/', views.add_address,name="add_address"),
    path('edit_address/<int:id>', views.edit_address, name="edit_address"),
    path('delete_address/<int:id>',views.delete_address,name="delete_address"),
    path('add_to_cart/',views.add_tocart,name="add_to_cart"),
    path('cart_view',views.cart_view,name="cart_view")
    ]