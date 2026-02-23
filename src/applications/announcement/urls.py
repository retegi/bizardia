from django.urls import path
from .views import announcement_detail

app_name = "announcement"

urlpatterns = [
    path("<slug:slug>/", announcement_detail, name="detail"),
]
