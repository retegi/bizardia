from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView
from .models import Reservation, ReservationSlot
from collections import defaultdict
from datetime import date
from django.views.generic import TemplateView
from django.utils.timezone import localtime
from .forms import ReservationForm
from django.utils import timezone
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views import View
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.core.mail import EmailMessage
from django.conf import settings

import base64
import json


class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'diningroom/diningroom.html'
    success_url = reverse_lazy('diningroom_app:reservation_success')

    def form_valid(self, form):
        user = self.request.user

        try:
            with transaction.atomic():

                reservation = form.save(commit=False)
                reservation.user = user
                reservation.save()

                activities = form.cleaned_data.get("activities")
                selected_tables = form.cleaned_data.get("selected_tables", [])
                room_urkabe = form.cleaned_data.get("room_urkabe", False)
                room_goiko = form.cleaned_data.get("room_goiko", False)
                fires = form.cleaned_data.get("fires", 0)
                ovens = form.cleaned_data.get("ovens", 0)
                barbacue = form.cleaned_data.get("barbacue", False)
                is_birthday = form.cleaned_data.get("is_birthday", False)

                for slot in activities:
                    reservation_slot = ReservationSlot(
                        reservation=reservation,
                        time_slot=slot,
                        selected_tables=selected_tables,
                        room_urkabe=room_urkabe,
                        room_goiko=room_goiko,
                        fires=fires,
                        ovens=ovens,
                        barbacue=barbacue,
                        is_birthday=is_birthday,
                    )

                    reservation_slot.full_clean()
                    reservation_slot.save()

            self.object = reservation
            return super().form_valid(form)

        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)


class ReservationListView(TemplateView):
    template_name = 'diningroom/reservations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        selected_date = self.request.GET.get("date")
        show_all = self.request.GET.get("all")

        reservations = None

        if selected_date:
            reservations = Reservation.objects.filter(
                reservation_date=selected_date
            ).prefetch_related("slots").order_by("reservation_date")

        elif show_all == "1":
            reservations = Reservation.objects.all().prefetch_related("slots").order_by("reservation_date")

        context["reservations"] = reservations
        context["selected_date"] = selected_date

        return context










class UserReservationListView(LoginRequiredMixin, TemplateView):
    template_name = 'diningroom/user_reservations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.localdate()

        reservations = (
            Reservation.objects
            .filter(
                user=self.request.user,
                reservation_date__gte=today
            )
            .prefetch_related(
                Prefetch(
                    'slots',
                    queryset=ReservationSlot.objects.order_by('time_slot')
                )
            )
            .order_by('reservation_date')
        )

        context['reservations'] = reservations
        return context


    
class ReservationDeleteView(LoginRequiredMixin,DeleteView):
    model = Reservation
    template_name = 'diningroom/confirm_delete.html'  # Puedes crear esta plantilla o redirigir directamente
    success_url = reverse_lazy('diningroom_app:user_reservations')  # Ajusta al nombre real de la vista "mis reservas"

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

class ReservationAvailabilityView(LoginRequiredMixin, View):

    def get(self, request):
        date = request.GET.get("date")
        time_slots = request.GET.getlist("time_slots[]")

        if not date or not time_slots:
            return JsonResponse({"error": "Missing parameters"}, status=400)

        slots = ReservationSlot.objects.filter(
            reservation__reservation_date=date,
            time_slot__in=time_slots
        )

        occupied_tables = []
        total_ovens = 0
        total_fires = 0
        urkabe_taken = False
        goiko_taken = False
        barbacue_taken = False

        for slot in slots:
            occupied_tables.extend(slot.selected_tables)
            total_ovens += slot.ovens
            total_fires += slot.fires
            if slot.room_urkabe:
                urkabe_taken = True
            if slot.room_goiko:
                goiko_taken = True
            if slot.barbacue:
                barbacue_taken = True

        return JsonResponse({
            "occupied_tables": list(set(occupied_tables)),
            "urkabe_taken": urkabe_taken,
            "goiko_taken": goiko_taken,
            "barbacue_taken": barbacue_taken,
            "ovens_available": max(0, 2 - total_ovens),
            "fires_available": max(0, 4 - total_fires),
        })


@login_required
def collective_payment_view(request):
    return render(request, "diningroom/collective_payment.html")


@login_required
@require_POST
@csrf_protect
def collective_payment_send_email(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    to_email = (payload.get("email") or "").strip()
    filename = (payload.get("filename") or "collective-payment.pdf").strip() or "collective-payment.pdf"
    pdf_base64 = payload.get("pdf_base64")

    if not to_email:
        return JsonResponse({"success": False, "error": "Missing email"}, status=400)
    if not pdf_base64:
        return JsonResponse({"success": False, "error": "Missing pdf"}, status=400)

    try:
        pdf_bytes = base64.b64decode(pdf_base64)
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid pdf encoding"}, status=400)

    subject = "Collective payment"
    body = "Adjunto encontrarás el PDF con el cálculo de pagos."

    try:
        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            to=[to_email],
        )
        msg.attach(filename, pdf_bytes, "application/pdf")
        sent = msg.send(fail_silently=False)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": True, "sent": sent})
