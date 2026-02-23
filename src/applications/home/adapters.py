from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        # Guarda usuario pero lo deja inactivo siempre
        user = super().save_user(request, user, form, commit=False)
        user.is_active = False
        if commit:
            user.save(update_fields=["is_active", "username", "email", "password"])
        return user

    def is_open_for_signup(self, request):
        return True  # Permite el registro

    def login(self, request, user):
        # Bloquea login si está inactivo
        if not user.is_active:
            raise PermissionDenied("Cuenta no activa. El administrador debe activarla.")
        return super().login(request, user)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return getattr(sociallogin.account, "provider", None) == "google"