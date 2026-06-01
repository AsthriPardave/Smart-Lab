from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='api-index'),
    path('health/', views.health_check, name='health-check'),
    path('validar-acceso/', views.validar_acceso, name='validar-acceso'),
]
