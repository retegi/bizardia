from django.urls import path
from . import views

app_name = 'activity_app'

urlpatterns = [
    path('', views.activity_list, name='activity_list'),
    path('crear/', views.activity_create, name='activity_create'),

    path(
        '<slug:slug>/',
        views.activity_detail,
        name='activity_detail'
    ),
    path(
        '<slug:slug>/register/',
        views.activity_register,
        name='activity_register'
    ),
    path(
        '<slug:slug>/registered/',
        views.activity_registered_list,
        name='activity_registered_list'
    ),
]
