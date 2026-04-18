from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('orders/', views.dashboard_orders, name='dashboard_orders'),
    path('orders/<int:order_id>/update/', views.dashboard_order_update, name='dashboard_order_update'),
    path('products/', views.dashboard_products, name='dashboard_products'),
]
