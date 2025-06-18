from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView
from .models import Reservation
from collections import defaultdict
from datetime import date
from django.views.generic import TemplateView
from collections import defaultdict
from django.utils.timezone import localtime
from .forms import ReservationForm
from collections import defaultdict
from django.utils import timezone
from django.db.models import Q

class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm  # Usa el formulario personalizado
    template_name = 'diningroom/diningroom.html'
    success_url = reverse_lazy('diningroom_app:reservation_success')

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Si `activities` viene en POST y no está en fields
        form.instance.activities = self.request.POST.getlist('activities')
        form.instance.custom_activity = self.request.POST.get('custom_activity', '')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print(form.errors)  # Verás el error en consola
        return super().form_invalid(form)

"""class ReservationListView(TemplateView):
    template_name = 'diningroom/reservations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservations = Reservation.objects.all().order_by('reservation_date')
        grouped = defaultdict(list)
        for r in reservations:
            grouped[r.reservation_date].append(r)

        context['grouped_reservations'] = dict(grouped)
        return context"""

class ReservationListView(TemplateView):
    template_name = 'diningroom/reservations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        reservations = Reservation.objects.filter(
            reservation_date__date__gte=today
        ).order_by('-reservation_date')
        context['reservations'] = reservations
        return context

class UserReservationListView(TemplateView):
    template_name = 'diningroom/user_reservations.html'  # Puedes usar otro template si deseas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        user = self.request.user
        reservations = Reservation.objects.filter(
            user=user,  # Filtra por el usuario logeado
            reservation_date__date__gte=today
        ).order_by('-reservation_date')
        context['reservations'] = reservations
        return context
    
class ReservationDeleteView(DeleteView):
    model = Reservation
    template_name = 'diningroom/confirm_delete.html'  # Puedes crear esta plantilla o redirigir directamente
    success_url = reverse_lazy('diningroom_app:user_reservations')  # Ajusta al nombre real de la vista "mis reservas"

