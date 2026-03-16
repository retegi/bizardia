from django.urls import path
from django.views.generic import TemplateView

from .views import (
    ReservationAvailabilityView,
    ReservationCreateView,
    ReservationDeleteView,
    ReservationListView,
    UserReservationListView,
    collective_payment_view,
    collective_payment_send_email,
)

app_name = 'diningroom_app'

urlpatterns = [
    path('', ReservationCreateView.as_view(), name='create_reservation'),
    path('success/', TemplateView.as_view(template_name='diningroom/reservation_success.html'), name='reservation_success'),
    path('reservations/', ReservationListView.as_view(), name='reservation_list'),
    path('my-reservations/', UserReservationListView.as_view(), name='user_reservations'),
    path('reservas/eliminar/<int:pk>/', ReservationDeleteView.as_view(), name='delete'),
    path('availability/', ReservationAvailabilityView.as_view(), name='reservation_availability'),
    path('collective-payment/', collective_payment_view, name='collective_payment'),
    path('collective-payment/send-email/', collective_payment_send_email, name='collective_payment_send_email'),
]