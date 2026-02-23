from django.contrib import admin
from .models import Reservation, ReservationSlot


# =====================================
#  INLINE PARA LAS FRANJAS
# =====================================

class ReservationSlotInline(admin.TabularInline):
    model = ReservationSlot
    extra = 0
    fields = (
        'time_slot',
        'selected_tables',
        'room_urkabe',
        'room_goiko',
        'fires',
        'ovens',
        'barbacue',
        'is_birthday',
    )
    show_change_link = True


# =====================================
#  ADMIN DE RESERVA PRINCIPAL
# =====================================

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):

    list_display = (
        'reservation_date',
        'user',
        'membership_number',
        'num_diners',
        'created_at',
        'get_time_slots',
    )

    list_filter = (
        'reservation_date',
        'created_at',
    )

    search_fields = (
        'membership_number',
        'user__username',
        'user__email',
    )

    ordering = ('-reservation_date', '-created_at')

    inlines = [ReservationSlotInline]

    date_hierarchy = 'reservation_date'

    def get_time_slots(self, obj):
        return ", ".join([slot.get_time_slot_display() for slot in obj.slots.all()])
    get_time_slots.short_description = "Franjas"


# =====================================
#  ADMIN DE FRANJAS (DETALLE)
# =====================================

@admin.register(ReservationSlot)
class ReservationSlotAdmin(admin.ModelAdmin):

    list_display = (
        'reservation_date',
        'time_slot',
        'reservation',
        'room_urkabe',
        'room_goiko',
        'fires',
        'ovens',
        'barbacue',
    )

    list_filter = (
        'time_slot',
        'room_urkabe',
        'room_goiko',
        'barbacue',
    )

    search_fields = (
        'reservation__membership_number',
        'reservation__user__username',
    )

    ordering = ('-reservation__reservation_date',)

    def reservation_date(self, obj):
        return obj.reservation.reservation_date

    reservation_date.short_description = "Fecha"
