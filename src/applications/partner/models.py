from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Erabiltzailea")
    )

    avatar = models.ImageField(
        _("Avatar"),
        upload_to="avatars/",
        null=True,
        blank=True,
    )

    partner_number = models.PositiveIntegerField(
        _("Bazkide zenbakia"),
        unique=True,
        null=True,
        blank=True
    )

    movil = models.CharField(
        _("Telefono mugikorra"),
        max_length=20,
        null=True,
        blank=True
    )

    movil2 = models.CharField(
        _("Bigarren mugikorra"),
        max_length=20,
        null=True,
        blank=True
    )

    address = models.CharField(
        _("Helbidea"),
        max_length=255,
        null=True,
        blank=True
    )

    date_of_birth = models.DateField(
        _("Jaiotze-data"),
        null=True,
        blank=True
    )

    partner_date = models.DateField(
        _("Bazkide-data"),
        null=True,
        blank=True
    )

    related_partner = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_profiles',
        verbose_name=_("Lotutako bazkidea")
    )

    class Meta:
        verbose_name = _("Bazkidea")
        verbose_name_plural = _("Bazkideak")

    def __str__(self):
        if self.user_id:
            name = (
                self.user.get_full_name()
                or self.user.email
                or self.user.username
                or f"User#{self.user_id}"
            )
        else:
            name = _("Lotu gabeko erabiltzailea")

        num = self.partner_number if self.partner_number is not None else "—"
        return f"{name} ({num})"