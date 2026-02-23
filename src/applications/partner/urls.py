from django.urls import path, include
from .views import SignupPendingView, partner_list

app_name = "partner_app"

urlpatterns = [
    path('registro/pending/', SignupPendingView.as_view(), name='signup_pending'),
    path("socios/", partner_list, name="partner_list"),
]
