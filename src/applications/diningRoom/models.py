from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q


# ================================
#  RESERVA PRINCIPAL (CABECERA)
# ================================

class Reservation(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Erabiltzailea")
    )

    # Fecha para la que se reserva
    reservation_date = models.DateField(
        _("Erreserba-data")
    )

    # Fecha y hora en la que se realiza la reserva
    created_at = models.DateTimeField(
        _("Sortze-data"),
        auto_now_add=True
    )

    membership_number = models.CharField(
        _("Bazkide zenbakia"),
        max_length=20
    )

    num_diners = models.PositiveIntegerField(
        _("Jankide kopurua")
    )

    class Meta:
        verbose_name = _("Erreserba")
        verbose_name_plural = _("Erreserbak")
        ordering = ['-reservation_date', '-created_at']

    def __str__(self):
        return f"{self.reservation_date} - {self.user.username}"


# ================================
#  FRANJAS DE RESERVA (DETALLE)
# ================================

class ReservationSlot(models.Model):

    TIME_CHOICES = [
        ('breakfast', _('Breakfast')),
        ('lunch', _('Lunch')),
        ('midday', _('Midday meal')),
        ('merienda', _('Merienda')),
        ('dinner', _('Dinner')),
        ('other', _('Other activity')),
    ]

    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="slots",
        verbose_name=_("Erreserba")
    )

    time_slot = models.CharField(
        _("Denbora-tartea"),
        max_length=20,
        choices=TIME_CHOICES
    )

    # Mesas seleccionadas (ej: ["7", "8"])
    selected_tables = models.JSONField(
        _("Hautatutako mahaiak"),
        default=list
    )

    # Salas
    room_urkabe = models.BooleanField(
        _("Urkabe gela"),
        default=False
    )

    room_goiko = models.BooleanField(
        _("Goiko gela"),
        default=False
    )

    # Recursos numéricos
    fires = models.PositiveIntegerField(
        _("Sukaldeko suak"),
        default=0
    )

    ovens = models.PositiveIntegerField(
        _("Labeak"),
        default=0
    )

    # Barbakoa (única)
    barbacue = models.BooleanField(
        _("Barbakoa"),
        default=False
    )

    # Cumpleaños
    is_birthday = models.BooleanField(
        _("Urtebetetze ospakizuna"),
        default=False
    )

    class Meta:
        verbose_name = _("Erreserba-tartea")
        verbose_name_plural = _("Erreserba-tarteak")
        unique_together = ('reservation', 'time_slot')
        indexes = [
            models.Index(fields=['time_slot']),
        ]

    def __str__(self):
        return f"{self.reservation.reservation_date} - {self.time_slot}"

    def get_time_order(self):
        order = {
            'breakfast': 1,
            'lunch': 2,
            'midday': 3,
            'merienda': 4,
            'dinner': 5,
            'other': 6,
        }
        return order.get(self.time_slot, 99)

    def clean(self):
        """
        Valida que no haya conflictos en:
        - Mesas
        - Salas
        - Barbakoa
        - Hornos (máx 2)
        - Fuegos (máx 4)
        """

        reservation_date = self.reservation.reservation_date

        # Buscar otros slots en la misma fecha y franja
        existing_slots = ReservationSlot.objects.filter(
            reservation__reservation_date=reservation_date,
            time_slot=self.time_slot
        ).exclude(pk=self.pk)

        # ===============================
        # 🔴 VALIDAR MESAS
        # ===============================
        for slot in existing_slots:
            if set(slot.selected_tables) & set(self.selected_tables):
                raise ValidationError("One of the selected tables is already reserved for this time slot.")

        # ===============================
        # 🔴 VALIDAR SALAS
        # ===============================
        if self.room_urkabe:
            if existing_slots.filter(room_urkabe=True).exists():
                raise ValidationError("Sala Urkabe is already reserved for this time slot.")

        if self.room_goiko:
            if existing_slots.filter(room_goiko=True).exists():
                raise ValidationError("Sala Goikoa is already reserved for this time slot.")

        # ===============================
        # 🔴 VALIDAR BARBACOA (ÚNICA)
        # ===============================
        if self.barbacue:
            if existing_slots.filter(barbacue=True).exists():
                raise ValidationError("Barbacue is already reserved for this time slot.")

        # ===============================
        # 🔴 VALIDAR HORNOS (MÁX 2)
        # ===============================
        total_ovens = sum(slot.ovens for slot in existing_slots) + self.ovens
        if total_ovens > 2:
            raise ValidationError("There are not enough ovens available for this time slot.")

        # ===============================
        # 🔴 VALIDAR FUEGOS (MÁX 4)
        # ===============================
        total_fires = sum(slot.fires for slot in existing_slots) + self.fires
        if total_fires > 4:
            raise ValidationError("There are not enough fires available for this time slot.")

