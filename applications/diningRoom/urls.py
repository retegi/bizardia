from django.urls import path
from .views import ReservationCreateView
from django.views.generic import TemplateView
from django.urls import path
from .views import ReservationListView, UserReservationListView, ReservationDeleteView

app_name = 'diningroom_app'

urlpatterns = [
    path('', ReservationCreateView.as_view(), name='create_reservation'),
    path('success/', TemplateView.as_view(template_name='diningroom/reservation_success.html'), name='reservation_success'),
    path('reservations/', ReservationListView.as_view(), name='reservation_list'),
    path('my-reservations/', UserReservationListView.as_view(), name='user_reservations'),
    path('reservas/eliminar/<int:pk>/', ReservationDeleteView.as_view(), name='delete'),

]