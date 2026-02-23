# applications/news/admin.py
from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content', 'author')
