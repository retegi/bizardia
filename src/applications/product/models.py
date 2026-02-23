from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(
        _("Izena"),
        max_length=100,
        unique=True
    )

    description = models.TextField(
        _("Deskribapena"),
        blank=True
    )

    image = models.ImageField(
        _("Irudia"),
        upload_to='categories/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        _("Sortze-data"),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _("Kategoria")
        verbose_name_plural = _("Kategoriak")

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_("Kategoria")
    )

    name = models.CharField(
        _("Izena"),
        max_length=100
    )

    code = models.CharField(
        _("Kodea"),
        max_length=50,
        unique=True
    )

    description = models.TextField(
        _("Deskribapena"),
        blank=True
    )

    price = models.DecimalField(
        _("Prezioa"),
        max_digits=7,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(
        _("Stocka"),
        default=0
    )

    is_active = models.BooleanField(
        _("Aktibo"),
        default=True
    )

    image = models.ImageField(
        _("Irudia"),
        upload_to='products/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        _("Sortze-data"),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _("Produktua")
        verbose_name_plural = _("Produktuak")

    def __str__(self):
        return self.name
