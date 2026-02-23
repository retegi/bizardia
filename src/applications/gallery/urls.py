from os import name
from django.urls import include, path
from . import views


app_name = 'gallery_app'

urlpatterns = [

    path('', views.gallery_list, name='gallery_list'),
    path('crear/', views.gallery_create, name='gallery_create'),
    path('<int:pk>/', views.gallery_detail, name='gallery_detail'),  # <-- este es el cambio

]