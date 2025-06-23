from django.db import models
from tinymce.models import HTMLField

class Gallery(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateTimeField(null=True, blank=True)
    content = HTMLField(blank=True, null=True)  # Editor WYSIWYG aquí
    short = models.TextField(blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='gallery/', blank=True, null=True)
    author = models.CharField(max_length=100)
    published = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.title
