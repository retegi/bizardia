from django import forms
from .models import WarehouseOrder, WarehouseOrderItem
from django.forms import inlineformset_factory

class WarehouseOrderForm(forms.ModelForm):
    class Meta:
        model = WarehouseOrder
        fields = ['notes']

WarehouseOrderItemFormSet = inlineformset_factory(
    WarehouseOrder,
    WarehouseOrderItem,
    fields=('product', 'quantity_requested', 'unit_price'),
    extra=1,
    can_delete=False
)