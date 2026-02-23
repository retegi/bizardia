from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Reservation, ReservationSlot


class ReservationForm(forms.ModelForm):
    # Franjas (se puede seleccionar varias)
    activities = forms.MultipleChoiceField(
        label=_("Select your activities"),
        choices=ReservationSlot.TIME_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    # Recursos (se aplicarán a cada franja seleccionada)
    selected_tables = forms.CharField(
        label=_("Selected tables (JSON)"),
        required=False,
        widget=forms.HiddenInput
    )

    room_urkabe = forms.BooleanField(required=False)
    room_goiko = forms.BooleanField(required=False)

    fires = forms.IntegerField(
        label=_("How many fires?"),
        min_value=0,
        max_value=4,
        required=False,
        initial=0
    )

    ovens = forms.IntegerField(
        label=_("How many ovens?"),
        min_value=0,
        max_value=2,
        required=False,
        initial=0
    )

    barbacue = forms.BooleanField(required=False)
    is_birthday = forms.BooleanField(required=False)

    class Meta:
        model = Reservation
        fields = ["reservation_date", "membership_number", "num_diners"]

    def clean_selected_tables(self):
        """
        Llega como string JSON desde el hidden input.
        Lo dejamos como lista real para que la view cree slots bien.
        """
        import json

        value = self.cleaned_data.get("selected_tables", "") or "[]"

        if isinstance(value, list):
            return value

        try:
            tables = json.loads(value)
            if not isinstance(tables, list):
                raise forms.ValidationError(_("Invalid tables format."))
            # normalizamos a strings ("7", "8")
            return [str(t) for t in tables]
        except Exception:
            raise forms.ValidationError(_("Invalid tables format."))