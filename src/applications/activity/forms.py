from django import forms
from .models import Activity
from .models import ActivityRegistration
from django.utils.translation import gettext_lazy as _


from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Activity, ActivityRegistration, YesNo



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
            "currency",
            "requires_payment",
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
            "currency": forms.TextInput(attrs={"class": "form-control"}),
            "requires_payment": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_price": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "show_registration_button": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "audience": forms.Select(attrs={"class": "form-select"}),
            "audience_note": forms.TextInput(attrs={"class": "form-control"}),
        }

class ActivityRegistrationForm(forms.ModelForm):
    pay_on_event = forms.BooleanField(
        label=_("Pagaré el día del evento"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

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
            'federation_member': forms.RadioSelect(attrs={'class': 'btn-check'}),
            'anonymous': forms.RadioSelect(attrs={'class': 'btn-check'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Federación → obligatorio y sin opción vacía
        self.fields['federation_member'].choices = YesNo.choices
        self.fields['federation_member'].required = True

        # Anónimo → sin opción vacía y default = "no"
        self.fields['anonymous'].choices = YesNo.choices
        self.fields['anonymous'].initial = YesNo.NO
