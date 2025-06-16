from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'partner_number', 'movil', 'movil2', 'address',
        'date_of_birth', 'partner_date', 'related_partner'
    )
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'partner_number', 'movil')
    list_filter = ('partner_date',)
