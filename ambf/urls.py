from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('apijoy/', views.apijoy),
    path('apimg/', views.apimg),
]