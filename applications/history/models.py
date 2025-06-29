from django.db import models
from django.utils.text import slugify
from tinymce.models import HTMLField

class History(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    content = HTMLField(blank=True, null=True)  # Editor WYSIWYG aquí
    short = models.TextField(blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='history/', blank=True, null=True)
    author = models.CharField(max_length=100)
    published = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)