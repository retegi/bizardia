from django.urls import path
from .views import SignupPendingView, partner_list, my_profile, my_profile_edit

app_name = "partner_app"

urlpatterns = [
    path('registro/pending/', SignupPendingView.as_view(), name='signup_pending'),
    path("socios/", partner_list, name="partner_list"),
    path("my-profile/", my_profile, name="my_profile"),
    path("my-profile/edit/", my_profile_edit, name="my_profile_edit"),
]
