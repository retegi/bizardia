from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    activities = forms.MultipleChoiceField(
        choices=[
            ('breakfast', 'Breakfast'),
            ('lunch', 'Lunch'),
            ('midday', 'Midday meal'),
            ('merienda', 'Merienda'),
            ('dinner', 'Dinner'),
            ('other', 'Other activity'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Reservation
        exclude = ['user']