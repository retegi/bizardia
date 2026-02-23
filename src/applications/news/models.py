from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from tinymce.models import HTMLField


class News(models.Model):

    VISIBILITY_CHOICES = [
        ("public", _("Publikoa")),
        ("members", _("Bazkideentzat bakarrik")),
    ]

    title = models.CharField(
        _("Izenburua"),
        max_length=200
    )

    slug = models.SlugField(
        _("Slug"),
        unique=True,
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

    image = models.ImageField(
        _("Irudia"),
        upload_to='news/',
        blank=True,
        null=True
    )

    author = models.CharField(
        _("Egilea"),
        max_length=100
    )

    # 🔐 NUEVO
    visibility = models.CharField(
        _("Ikusgarritasuna"),
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="public"
    )

    published = models.BooleanField(
        _("Argitaratua"),
        default=False
    )

    published_at = models.DateTimeField(
        _("Argitaratze-data"),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _("Albistea")
        verbose_name_plural = _("Albisteak")
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
