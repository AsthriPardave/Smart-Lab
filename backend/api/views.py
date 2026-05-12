from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Docente, Dispositivo, Laboratorio, Horario, RegistroAcceso
from .serializers import (
    DocenteSerializer, DispositivoSerializer, LaboratorioSerializer,
    HorarioSerializer, RegistroAccesoSerializer, RegistroAccesoCreateSerializer
)


@api_view(['GET'])
def health_check(request):
    """
    Endpoint para verificar el estado de la API
    """
    return Response({
        'status': 'ok',
        'message': 'SmartLab API is running'
    }, status=status.HTTP_200_OK)


class DocenteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar docentes
    """
    queryset = Docente.objects.all()
    serializer_class = DocenteSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activo', 'codigo_docente']
    search_fields = ['nombres', 'correo', 'codigo_docente']
    ordering_fields = ['nombres', 'codigo_docente', 'created_at']
    ordering = ['nombres']
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """
        Endpoint para listar solo docentes activos
        """
        docentes = self.queryset.filter(activo=True)
        serializer = self.get_serializer(docentes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def horarios(self, request, pk=None):
        """
        Obtener horarios de un docente específico
        """
        docente = self.get_object()
        horarios = docente.horarios.all()
        serializer = HorarioSerializer(horarios, many=True)
        return Response(serializer.data)


class DispositivoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar dispositivos
    """
    queryset = Dispositivo.objects.all()
    serializer_class = DispositivoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['estado', 'codigo']
    search_fields = ['codigo', 'ip']
    ordering_fields = ['codigo', 'created_at']
    ordering = ['codigo']


class LaboratorioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar laboratorios
    """
    queryset = Laboratorio.objects.select_related('dispositivo').all()
    serializer_class = LaboratorioSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['estado', 'nombre']
    search_fields = ['nombre', 'ubicacion']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['nombre']
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """
        Endpoint para listar solo laboratorios activos
        """
        laboratorios = self.queryset.filter(estado=True)
        serializer = self.get_serializer(laboratorios, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def horarios(self, request, pk=None):
        """
        Obtener horarios de un laboratorio específico
        """
        laboratorio = self.get_object()
        horarios = laboratorio.horarios.all()
        serializer = HorarioSerializer(horarios, many=True)
        return Response(serializer.data)


class HorarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar horarios
    """
    queryset = Horario.objects.select_related('docente', 'laboratorio').all()
    serializer_class = HorarioSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['dia_semana', 'docente', 'laboratorio']
    search_fields = ['docente__nombres', 'laboratorio__nombre']
    ordering_fields = ['dia_semana', 'hora_inicio']
    ordering = ['dia_semana', 'hora_inicio']
    
    @action(detail=False, methods=['get'])
    def por_dia(self, request):
        """
        Filtrar horarios por día de la semana
        """
        dia = request.query_params.get('dia', None)
        if dia:
            horarios = self.queryset.filter(dia_semana__iexact=dia)
            serializer = self.get_serializer(horarios, many=True)
            return Response(serializer.data)
        return Response({'error': 'Parámetro "dia" requerido'}, status=status.HTTP_400_BAD_REQUEST)


class RegistroAccesoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar registros de acceso
    """
    queryset = RegistroAcceso.objects.select_related('docente', 'laboratorio').all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['acceso_permitido', 'docente', 'laboratorio']
    search_fields = ['docente__nombres', 'laboratorio__nombre', 'motivo']
    ordering_fields = ['fecha_hora']
    ordering = ['-fecha_hora']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RegistroAccesoCreateSerializer
        return RegistroAccesoSerializer
    
    @action(detail=False, methods=['get'])
    def recientes(self, request):
        """
        Obtener los últimos 50 registros de acceso
        """
        registros = self.queryset[:50]
        serializer = self.get_serializer(registros, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_fecha(self, request):
        """
        Filtrar registros por rango de fechas
        """
        fecha_inicio = request.query_params.get('fecha_inicio', None)
        fecha_fin = request.query_params.get('fecha_fin', None)
        
        if fecha_inicio and fecha_fin:
            registros = self.queryset.filter(
                fecha_hora__date__gte=fecha_inicio,
                fecha_hora__date__lte=fecha_fin
            )
            serializer = self.get_serializer(registros, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Parámetros "fecha_inicio" y "fecha_fin" requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )
