from django.contrib import admin
from django.utils.html import format_html
from .models import Gallery

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at', 'photoDate', 'slug', 'image_tag')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'author')
    list_filter = ('published_at', 'photoDate')
    readonly_fields = ('published_at', 'image_tag')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'author', 'photoDate', 'image', 'image_tag')
        }),
        ('Información automática', {
            'fields': ('published_at',),
            'classes': ('collapse',),
        }),
    )

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "No Image"

    image_tag.short_description = 'Vista previa'

