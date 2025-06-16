from django.contrib import admin
from .models import Activity

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content', 'author')