from django.urls import path
from .views import ProductListView, OrderCreateView, OrderDetailView
from .views import WarehouseOrderCreateView
from .views import WarehouseOrderListView

app_name = 'warehouse'

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product_list'),
    path('orders/new/', OrderCreateView.as_view(), name='create_order'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('create-order/', WarehouseOrderCreateView.as_view(), name='create_order'),
    path('orders/', WarehouseOrderListView.as_view(), name='order_list'),
]