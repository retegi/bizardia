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
        '<slug:slug>/checkout/',
        views.activity_checkout,
        name='activity_checkout'
    ),
    path(
        '<slug:slug>/checkout/success/',
        views.activity_checkout_success,
        name='activity_checkout_success'
    ),
    path(
        '<slug:slug>/checkout/cancel/',
        views.activity_checkout_cancel,
        name='activity_checkout_cancel'
    ),
    path(
        '<slug:slug>/registered/',
        views.activity_registered_list,
        name='activity_registered_list'
    ),
]
