from django.contrib import admin
from .models import Docente, Dispositivo, Laboratorio, Horario, RegistroAcceso


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ['codigo_docente', 'nombres', 'correo', 'activo', 'fingerprint']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombres', 'correo', 'codigo_docente']
    ordering = ['nombres']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'ip', 'estado', 'created_at']
    list_filter = ['estado', 'created_at']
    search_fields = ['codigo', 'ip']
    ordering = ['codigo']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ubicacion', 'dispositivo', 'estado', 'created_at']
    list_filter = ['estado', 'created_at']
    search_fields = ['nombre', 'ubicacion']
    ordering = ['nombre']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ['docente', 'laboratorio', 'dia_semana', 'hora_inicio', 'hora_fin']
    list_filter = ['dia_semana', 'created_at']
    search_fields = ['docente__nombres', 'laboratorio__nombre']
    ordering = ['dia_semana', 'hora_inicio']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['docente', 'laboratorio']


@admin.register(RegistroAcceso)
class RegistroAccesoAdmin(admin.ModelAdmin):
    list_display = ['docente', 'laboratorio', 'fecha_hora', 'acceso_permitido', 'motivo']
    list_filter = ['acceso_permitido', 'fecha_hora', 'laboratorio']
    search_fields = ['docente__nombres', 'laboratorio__nombre', 'motivo']
    ordering = ['-fecha_hora']
    readonly_fields = ['fecha_hora']
    autocomplete_fields = ['docente', 'laboratorio']
    date_hierarchy = 'fecha_hora'
