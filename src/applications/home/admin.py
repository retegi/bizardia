from django.contrib import admin
from django.utils.html import format_html
from .models import HomeContent


# blog/admin.py
from django.contrib import admin
from .models import HomeContent


@admin.register(HomeContent)
class HomeContentAdmin(admin.ModelAdmin):

    fieldsets = (

        ("Visibility", {
            "fields": (
                "show_welcome_section",
                "show_director_section",
                "show_membership_section",
                "show_membership_button",
            )
        }),

        ("Director Section", {
            "fields": (
                "director_name",
                "director_position",
                "director_welcome_text",
                "director_image",
            )
        }),

        ("Contact Information", {
            "fields": (
                "phone",
                "email",
                "address",
            )
        }),

        ("Association Info", {
            "fields": (
                "association_name",
                "slogan",
                "foundation_year",
                "number_of_members",
                "activities_per_year",
            )
        }),

        ("Membership Section", {
            "fields": (
                "membership_button_text",
                "membership_info_text",
                "membership_button_url",
            )
        }),

        ("Control", {
            "fields": ("updated_at",),
        }),
    )

    readonly_fields = ("updated_at",)


    # =========================
    # Image preview
    # =========================
    def preview_image(self, obj):
        if obj.director_image:
            return format_html(
                '<img src="{}" style="max-height:150px; border-radius:8px;" />',
                obj.director_image.url
            )
        return "No image"

    preview_image.short_description = "Image preview"

    # =========================
    # Singleton protection
    # =========================
    def has_add_permission(self, request):
        # Solo permitir una instancia
        if HomeContent.objects.exists():
            return False
        return True
