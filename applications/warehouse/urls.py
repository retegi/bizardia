from django.urls import path
from .views import ProductListView, OrderCreateView, OrderDetailView

app_name = 'warehouse'

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product_list'),
    path('orders/new/', OrderCreateView.as_view(), name='create_order'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
]