from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True  # Permite registros si lo deseas

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.is_active = False  # Desactiva usuario por defecto
        if commit:
            user.save()
        return user
