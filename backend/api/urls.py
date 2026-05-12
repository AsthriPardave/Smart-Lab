from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear el router y registrar los viewsets
router = DefaultRouter()
router.register(r'docentes', views.DocenteViewSet, basename='docente')
router.register(r'dispositivos', views.DispositivoViewSet, basename='dispositivo')
router.register(r'laboratorios', views.LaboratorioViewSet, basename='laboratorio')
router.register(r'horarios', views.HorarioViewSet, basename='horario')
router.register(r'registros-acceso', views.RegistroAccesoViewSet, basename='registro-acceso')

urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    path('', include(router.urls)),
]
