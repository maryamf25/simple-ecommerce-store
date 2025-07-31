from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('update_cart/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout_view/', views.checkout_view, name='checkout_view'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('checkout/buy-now/', views.checkout_buy_now, name='checkout_buy_now'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('accounts/profile/', views.profile, name='profile'),
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
path('logout/', views.logout_success, name='logout'), 
path('dashboard/', views.dashboard, name='user_dashboard'),

 
    path('orders/', views.view_orders, name='view_orders'),

]
