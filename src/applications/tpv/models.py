from django.db import models
from django.conf import settings
from decimal import Decimal

class Ticket(models.Model):
    partner = models.ForeignKey(
        'partner.Profile',
        on_delete=models.PROTECT,
        related_name='tickets',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)

    total = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    def calculate_total(self):
        total = sum(item.get_total() for item in self.items.all())
        self.total = total
        self.save(update_fields=['total'])
        return total

    def __str__(self):
        return f"Ticket #{self.id} - {self.partner}"


class TicketItem(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2
    )

    def get_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Payment(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('other', 'Otro'),
    )

    ticket = models.OneToOneField(
        Ticket,
        related_name='payment',
        on_delete=models.CASCADE
    )
    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago Ticket #{self.ticket.id} ({self.method})"
