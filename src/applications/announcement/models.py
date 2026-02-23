from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone


class Announcement(models.Model):

    VISIBILITY_CHOICES = [
        ("public", _("Publikoa")),
        ("members", _("Bazkideentzat bakarrik")),
        ("board", _("Zuzendaritzarentzat bakarrik")),
    ]

    # =========================
    # Content
    # =========================
    title = models.CharField(
        _("Izenburua"),
        max_length=200
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    content = models.TextField(
        _("Edukia"),
        blank=True,
        null=True
    )

    short_text = models.CharField(
        _("Testu laburra (bannerrean)"),
        max_length=255,
        blank=True,
        help_text=_("If empty, title will be shown in banner.")
    )

    # =========================
    # Visibility
    # =========================
    visibility = models.CharField(
        _("Ikusgarritasuna"),
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="members"
    )

    # =========================
    # Schedule
    # =========================
    start_date = models.DateTimeField(
        _("Hasiera data")
    )

    end_date = models.DateTimeField(
        _("Amaiera data")
    )

    active = models.BooleanField(
        _("Aktiboa"),
        default=True
    )

    priority = models.PositiveIntegerField(
        _("Lehentasuna"),
        default=0,
        help_text=_("Higher number = shown first")
    )

    # =========================
    # Styling (optional but useful)
    # =========================
    banner_style = models.CharField(
        _("Banner estiloa"),
        max_length=20,
        choices=[
            ("info", "Info (blue)"),
            ("warning", "Warning (yellow)"),
            ("danger", "Danger (red)"),
            ("success", "Success (green)"),
        ],
        default="warning"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Komunikatua")
        verbose_name_plural = _("Komunikatuak")
        ordering = ["-priority", "-start_date"]

    def __str__(self):
        return self.title

    def is_current(self):
        now = timezone.now()
        return (
            self.active and
            self.start_date <= now <= self.end_date
        )

    def get_banner_text(self):
        return self.short_text if self.short_text else self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Announcement.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
