from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

class History(models.Model):
    title = models.CharField(
        _("Izenburua"),
        max_length=200
    )

    slug = models.SlugField(
        _("Slug"),
        unique=True,
        blank=True
    )

    date = models.DateTimeField(
        _("Data"),
        null=True,
        blank=True
    )

    content = HTMLField(
        _("Edukia"),
        blank=True,
        null=True
    )

    short = models.TextField(
        _("Laburpena"),
        blank=True,
        null=True
    )

    published_at = models.DateTimeField(
        _("Argitaratze-data"),
        auto_now_add=True
    )

    image = models.ImageField(
        _("Irudia"),
        upload_to='history/',
        blank=True,
        null=True
    )

    author = models.CharField(
        _("Egilea"),
        max_length=100
    )

    published = models.BooleanField(
        _("Argitaratua"),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Historia")
        verbose_name_plural = _("Historia")

        # Alternativa si quieres plural explícito:
        # verbose_name_plural = _("Historia-elementuak")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
