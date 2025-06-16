from django.urls import path
from .views import SignupPendingView

urlpatterns = [
    path('registro/pending/', SignupPendingView.as_view(), name='signup_pending'),
]
