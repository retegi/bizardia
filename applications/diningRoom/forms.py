from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Reservation

class ReservationForm(forms.ModelForm):
    activities = forms.MultipleChoiceField(
        choices=[
            ('breakfast', _('Breakfast')),
            ('lunch', _('Lunch')),
            ('midday', _('Midday meal')),
            ('merienda', _('Merienda')),
            ('dinner', _('Dinner')),
            ('other', _('Other activity')),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Reservation
        exclude = ['user']
