from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'reservation_date', 'membership_number',
        'num_diners', 'selected_tables', 'room_urkabe',
        'room_goiko', 'is_birthday', 'fires',
        'ovens', 'barbacue'
    )
    list_filter = (
        'reservation_date', 'room_urkabe', 'room_goiko',
        'is_birthday', 'fires', 'ovens', 'barbacue'
    )
    ordering = ('reservation_date',)
    search_fields = ('membership_number', 'user__username')
