from django.urls import path
from . import views

app_name = 'tpv'

urlpatterns = [
    path('', views.tpv_view, name='tpv'),
    path('add-item/', views.add_item, name='add_item'),
    path("clear-ticket/", views.clear_ticket, name="clear_ticket"),
    path("update-qty/", views.update_quantity, name="update_quantity"),
    path("finalize/", views.finalize_ticket, name="finalize_ticket"),
    path("ticket/<int:pk>/pdf/", views.ticket_pdf_view, name="ticket_pdf"),
    path("my-tickets/", views.my_ticket_list, name="my_tickets"),
    path("my-tickets/<int:pk>/", views.my_ticket_detail, name="my_ticket_detail"),
]
