# applications/news/urls.py
from django.urls import path
from . import views

app_name = 'news_app'

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('create/', views.news_create, name='news_create'),
    path('<int:pk>/', views.news_detail, name='news_detail'),
]
