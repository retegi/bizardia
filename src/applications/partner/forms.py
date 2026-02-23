# applications/partner/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class ProfileAdminForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["user"].label_from_instance = (
            lambda u: f"{u.username} | {u.email} | {u.first_name} {u.last_name}"
        )
