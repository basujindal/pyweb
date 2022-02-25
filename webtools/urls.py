from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='webtools-home'),
    path('about/', views.about, name='webtools-about'),
]