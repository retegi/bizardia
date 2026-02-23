from django.contrib import admin
from .models import Activity, ActivityRegistration, ActivityImage
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib import messages


class ActivityRegistrationInline(admin.TabularInline):
    model = ActivityRegistration
    extra = 0
    readonly_fields = ("created_at",)


class ActivityImageInline(admin.TabularInline):
    model = ActivityImage
    extra = 1
    fields = ("image", "title", "order")
    ordering = ("order",)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "author", "status", "outstanding")
        }),
        (_("Contenido"), {
            "fields": ("short", "content", "cover_image")
        }),
        (_("Datos de la actividad"), {
            "fields": ("activity_date_time", "price", "show_price", "show_registration_button")
        }),
        (_("Participación"), {
            "fields": ("audience", "audience_note")
        }),
        (_("Publicación"), {
            "fields": ("published_at", "published_by"),
            "classes": ("collapse",),
        }),
    )

    list_display = (
        "title",
        "status",
        "is_published_flag",
        "outstanding",
        "activity_date_time",
        "audience_display",
        "published_at",
    )

    list_filter = (
        "status",
        "outstanding",
        "audience",
    )

    search_fields = ("title", "short", "content", "author")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ActivityImageInline, ActivityRegistrationInline]
    ordering = ("-published_at", "-created_at")

    @admin.display(description=_("Público"))
    def audience_display(self, obj):
        return obj.get_audience_display()

    @admin.display(boolean=True, description=_("Argitaratua"))
    def is_published_flag(self, obj):
        return obj.status == Activity.Status.PUBLISHED

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if not request.user.has_perm("activity.can_publish_activity"):
            ro += ["status", "published_at", "published_by"]
        return ro

    def save_model(self, request, obj, form, change):
        # Si el usuario tiene permiso de publicar
        if request.user.has_perm("activity.can_publish_activity"):
            if obj.status == Activity.Status.PUBLISHED:
                if obj.published_at is None:
                    obj.published_at = timezone.now()
                if obj.published_by_id is None:
                    obj.published_by = request.user
            else:
                # Si deja de estar publicada, limpiamos metadatos
                obj.published_at = None
                obj.published_by = None

        super().save_model(request, obj, form, change)


@admin.register(ActivityRegistration)
class ActivityRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "activity",
        "name",
        "surname",
        "locality",
        "federation_member",
        "anonymous",
        "user",
        "created_at",
    )

    list_filter = (
        "activity",
        "federation_member",
        "anonymous",
    )

    search_fields = (
        "name",
        "surname",
        "locality",
    )

    ordering = ("-created_at",)