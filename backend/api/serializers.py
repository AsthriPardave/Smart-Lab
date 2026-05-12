from rest_framework import serializers
from .models import Docente, Dispositivo, Laboratorio, Horario, RegistroAcceso


class DocenteSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Docente
    """
    class Meta:
        model = Docente
        fields = [
            'id', 'nombres', 'correo', 'codigo_docente', 
            'activo', 'fingerprint', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DispositivoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Dispositivo
    """
    class Meta:
        model = Dispositivo
        fields = ['id', 'codigo', 'ip', 'estado', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class LaboratorioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Laboratorio
    """
    dispositivo_detalle = DispositivoSerializer(source='dispositivo', read_only=True)
    
    class Meta:
        model = Laboratorio
        fields = [
            'id', 'nombre', 'ubicacion', 'estado', 
            'dispositivo', 'dispositivo_detalle', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class HorarioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Horario
    """
    docente_nombre = serializers.CharField(source='docente.nombres', read_only=True)
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    
    class Meta:
        model = Horario
        fields = [
            'id', 'dia_semana', 'hora_inicio', 'hora_fin',
            'docente', 'docente_nombre', 
            'laboratorio', 'laboratorio_nombre',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validar que la hora de inicio sea anterior a la hora de fin
        """
        if data.get('hora_inicio') and data.get('hora_fin'):
            if data['hora_inicio'] >= data['hora_fin']:
                raise serializers.ValidationError(
                    "La hora de inicio debe ser anterior a la hora de fin"
                )
        return data


class RegistroAccesoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo RegistroAcceso
    """
    docente_nombre = serializers.CharField(source='docente.nombres', read_only=True)
    docente_codigo = serializers.CharField(source='docente.codigo_docente', read_only=True)
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    
    class Meta:
        model = RegistroAcceso
        fields = [
            'id', 'fecha_hora', 'acceso_permitido', 'motivo',
            'docente', 'docente_nombre', 'docente_codigo',
            'laboratorio', 'laboratorio_nombre'
        ]
        read_only_fields = ['fecha_hora']


class RegistroAccesoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer específico para crear registros de acceso
    """
    class Meta:
        model = RegistroAcceso
        fields = ['docente', 'laboratorio', 'acceso_permitido', 'motivo']
