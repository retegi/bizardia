from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(_("Name"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Category"))
    unit = models.CharField(_("Unit"), max_length=50, default='unit')
    stock_level = models.PositiveIntegerField(_("Stock level"), default=0)
    min_stock = models.PositiveIntegerField(_("Minimum stock"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name




class WarehouseOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
    ]

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.created_at.strftime('%Y-%m-%d')}"

    def total_items(self):
        return sum(item.quantity_requested for item in self.items.all())


class WarehouseOrderItem(models.Model):
    order = models.ForeignKey(WarehouseOrder, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_requested = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    def subtotal(self):
        if self.unit_price:
            return self.unit_price * self.quantity_requested
        return 0
