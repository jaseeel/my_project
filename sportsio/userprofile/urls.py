from django.urls import path
from userprofile import views






#User_profile Urls

urlpatterns = [
    path('', views.user_profile,name="user_profile"),
    path('add_address/', views.add_address,name="add_address"),
    path('edit_address/<int:id>', views.edit_address, name="edit_address"),
    path('delete_address/<int:id>',views.delete_address,name="delete_address"),
    path('add_to_cart/',views.add_tocart,name="add_to_cart"),
    path('cart_view',views.cart_view,name="cart_view"),
    path('update_profile',views.update_profile,name='update_profile'),
    path('update_cart_quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('remove_cart/<int:id>',views.remove_cart,name="remove_cart"),
    path('reset_password/',views.reset_password,name="reset_password"),
    path('order_checkout/',views.order_checkout,name='order_checkout'),
    path('confirm_orders',views.confirm_orders,name='confirm_orders'),
    path('order_view/',views.order_view,name="order_view"),
    path("orders/<int:order_id>/", views.order_confirmation, name="order_confirmation"),
    path("cancel-order/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path("order_view/<int:id>/",views.order_view,name="order_view")
    ]