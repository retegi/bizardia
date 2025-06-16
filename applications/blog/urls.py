from os import name
from django.urls import include, path
from . import views


app_name = 'blog_app'

urlpatterns = [

    path('', views.blog_list, name='blog_list'),
    path('crear/', views.blog_create, name='blog_create'),
    path('<int:pk>/', views.blog_detail, name='blog_detail'),

]