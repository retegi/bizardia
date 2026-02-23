from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils import timezone

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "visibility",
        "active",
        "priority",
        "start_date",
        "end_date",
        "is_current_status",
    )

    list_filter = (
        "visibility",
        "active",
        "banner_style",
        "start_date",
    )

    search_fields = (
        "title",
        "content",
        "short_text",
    )

    prepopulated_fields = {"slug": ("title",)}

    ordering = ("-priority", "-start_date")

    readonly_fields = ("created_at",)

    fieldsets = (
        (_("Content"), {
            "fields": (
                "title",
                "slug",
                "content",
                "short_text",
            )
        }),

        (_("Visibility"), {
            "fields": (
                "visibility",
                "active",
                "priority",
                "banner_style",
            )
        }),

        (_("Schedule"), {
            "fields": (
                "start_date",
                "end_date",
            )
        }),

        (_("System"), {
            "fields": (
                "created_at",
            )
        }),
    )

    def is_current_status(self, obj):
        now = timezone.now()
        if obj.active and obj.start_date <= now <= obj.end_date:
            return format_html('<span style="color: green; font-weight: bold;">● Active Now</span>')
        return format_html('<span style="color: red;">● Not Active</span>')

    is_current_status.short_description = "Current Status"
