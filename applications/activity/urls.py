from os import name
from django.urls import include, path
from . import views


app_name = 'activity_app'

urlpatterns = [
    path('', views.activity_list, name='activity_list'),
    path('crear/', views.activity_create, name='activity_create'),
    path('<int:pk>/', views.activity_detail, name='activity_detail'),
]