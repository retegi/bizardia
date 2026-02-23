from django.urls import path
from . import views

app_name = 'tpv'

urlpatterns = [
    path('', views.tpv_view, name='tpv'),
    path('add-item/', views.add_item, name='add_item'),
    path("clear-ticket/", views.clear_ticket, name="clear_ticket"),
    path("update-qty/", views.update_quantity, name="update_quantity"),


]
