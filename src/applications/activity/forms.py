from django import forms
from .models import Activity
from .models import ActivityRegistration
from django.utils.translation import gettext_lazy as _


from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Activity, ActivityRegistration


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            "title",
            "short",
            "content",
            "cover_image",
            "author",
            "activity_date_time",
            "price",
            "show_price",
            "show_registration_button",
            "audience",
            "audience_note",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "short": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            # content es HTMLField (TinyMCE): normalmente no hace falta widget custom aquí
            "author": forms.TextInput(attrs={"class": "form-control"}),
            "activity_date_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "show_price": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_registration_button": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "audience": forms.Select(attrs={"class": "form-select"}),
            "audience_note": forms.TextInput(attrs={"class": "form-control"}),
        }

class ActivityRegistrationForm(forms.ModelForm):
    class Meta:
        model = ActivityRegistration
        fields = [
            'name',
            'surname',
            'locality',
            'federation_member',
            'anonymous',
        ]

        labels = {
            'name': _("Izena"),
            'surname': _("Abizena"),
            'locality': _("Herria"),
            'federation_member': _("Mendi federazioko kidea"),
            'anonymous': _("Erregistro anonimoa"),
        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'locality': forms.TextInput(attrs={'class': 'form-control'}),
            'federation_member': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
