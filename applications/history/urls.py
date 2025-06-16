from os import name
from django.urls import include, path
from . import views


app_name = 'history_app'

urlpatterns = [

    path('', views.history_list, name='history_list'),
    path('crear/', views.history_create, name='history_create'),
    path('<int:pk>/', views.history_detail, name='history_detail'),

]