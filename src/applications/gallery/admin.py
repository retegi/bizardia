from PIL import UnidentifiedImageError

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from .forms import MultipleGalleryImageUploadForm
from .models import Gallery, GalleryImage


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1
    fields = ("image", "title", "order")
    ordering = ("order",)


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "published",
        "featured",
        "published_at",
        "cover_image",
    )

    list_filter = (
        "published",
        "featured",
    )

    search_fields = (
        "title",
        "short",
        "content",
    )

    inlines = [GalleryImageInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "cover_image":
            object_id = request.resolver_match.kwargs.get("object_id")
            if object_id:
                kwargs["queryset"] = GalleryImage.objects.filter(gallery_id=object_id)
            else:
                kwargs["queryset"] = GalleryImage.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("gallery", "title", "order")
    list_filter = ("gallery",)
    change_list_template = "admin/gallery/galleryimage/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload-multiple/",
                self.admin_site.admin_view(self.upload_multiple_view),
                name="gallery_galleryimage_upload_multiple",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["upload_multiple_url"] = reverse(
            "admin:gallery_galleryimage_upload_multiple"
        )
        return super().changelist_view(request, extra_context=extra_context)

    def upload_multiple_view(self, request):
        if not self.has_add_permission(request):
            self.message_user(
                request,
                _("Ez daukazu irudiak gehitzeko baimenik."),
                level=messages.ERROR,
            )
            return redirect("admin:gallery_galleryimage_changelist")

        if request.method == "POST":
            form = MultipleGalleryImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                gallery = form.cleaned_data["gallery"]
                files = request.FILES.getlist("images")
                success_count = 0
                failed_count = 0

                last_order = (
                    GalleryImage.objects.filter(gallery=gallery)
                    .order_by("-order")
                    .values_list("order", flat=True)
                    .first()
                )
                next_order = (last_order + 1) if last_order is not None else 0

                for uploaded_file in files:
                    try:
                        image_obj = GalleryImage(
                            gallery=gallery,
                            image=uploaded_file,
                            title=MultipleGalleryImageUploadForm.title_from_filename(
                                uploaded_file.name
                            ),
                            order=next_order,
                        )
                        image_obj.full_clean()
                        image_obj.save()
                        success_count += 1
                        next_order += 1
                    except (ValidationError, UnidentifiedImageError, OSError) as exc:
                        failed_count += 1
                        self.message_user(
                            request,
                            _("Errorea %(name)s fitxategiarekin: %(error)s")
                            % {"name": uploaded_file.name, "error": str(exc)},
                            level=messages.WARNING,
                        )

                if success_count:
                    self.message_user(
                        request,
                        _("%(count)s irudi igo dira zuzen.") % {"count": success_count},
                        level=messages.SUCCESS,
                    )
                if failed_count:
                    self.message_user(
                        request,
                        _("%(count)s irudik huts egin dute.") % {"count": failed_count},
                        level=messages.WARNING,
                    )
                return redirect("admin:gallery_galleryimage_changelist")
        else:
            form = MultipleGalleryImageUploadForm()

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "form": form,
            "title": _("Subir varias fotos"),
            "changelist_url": reverse("admin:gallery_galleryimage_changelist"),
        }
        return render(request, "admin/gallery/galleryimage/upload_multiple.html", context)
