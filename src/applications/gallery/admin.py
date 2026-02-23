from django.contrib import admin
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
        "published_at",
    )

    list_filter = (
        "published",
    )

    search_fields = (
        "title",
        "short",
        "content",
    )

    inlines = [GalleryImageInline]



@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("gallery", "order")
