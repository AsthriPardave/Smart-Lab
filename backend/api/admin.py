from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Docente, Dispositivo, Laboratorio, Horario, RegistroAcceso


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ['codigo_docente', 'nombres', 'correo', 'fingerprint', 'estado_badge', 'total_accesos']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombres', 'correo', 'codigo_docente', 'fingerprint']
    ordering = ['nombres']
    readonly_fields = ['created_at', 'updated_at', 'total_accesos', 'ultimo_acceso']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombres', 'correo', 'codigo_docente')
        }),
        ('Información Biométrica', {
            'fields': ('fingerprint', 'activo')
        }),
        ('Estadísticas', {
            'fields': ('total_accesos', 'ultimo_acceso'),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activar_docentes', 'desactivar_docentes']
    
    @admin.display(description='Estado', ordering='activo')
    def estado_badge(self, obj):
        if obj.activo:
            return format_html('<span style="color: green; font-weight: bold;">✓ Activo</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Inactivo</span>')
    
    @admin.display(description='Total Accesos')
    def total_accesos(self, obj):
        return obj.registros_acceso.count()
    
    @admin.display(description='Último Acceso')
    def ultimo_acceso(self, obj):
        ultimo = obj.registros_acceso.filter(acceso_permitido=True).first()
        if ultimo:
            return ultimo.fecha_hora.strftime('%d/%m/%Y %H:%M')
        return 'Sin accesos'
    
    @admin.action(description='Activar docentes seleccionados')
    def activar_docentes(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} docente(s) activado(s) exitosamente.')
    
    @admin.action(description='Desactivar docentes seleccionados')
    def desactivar_docentes(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} docente(s) desactivado(s) exitosamente.')


@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'ip', 'laboratorio_asignado', 'estado_badge', 'created_at']
    list_filter = ['estado', 'created_at']
    search_fields = ['codigo', 'ip']
    ordering = ['codigo']
    readonly_fields = ['created_at', 'updated_at']
    
    @admin.display(description='Laboratorio', ordering='laboratorio')
    def laboratorio_asignado(self, obj):
        try:
            lab = obj.laboratorio
            return format_html('<strong>{}</strong> - {}', lab.nombre, lab.ubicacion)
        except:
            return format_html('<span style="color: orange;">Sin asignar</span>')
    
    @admin.display(description='Estado', ordering='estado')
    def estado_badge(self, obj):
        if obj.estado:
            return format_html('<span style="color: green; font-weight: bold;">✓ Activo</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Inactivo</span>')


@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ubicacion', 'dispositivo', 'estado_badge', 'total_horarios', 'accesos_hoy']
    list_filter = ['estado', 'created_at']
    search_fields = ['nombre', 'ubicacion']
    ordering = ['nombre']
    readonly_fields = ['created_at', 'updated_at', 'total_horarios', 'accesos_hoy', 'accesos_semana']
    
    fieldsets = (
        ('Información del Laboratorio', {
            'fields': ('nombre', 'ubicacion', 'dispositivo', 'estado')
        }),
        ('Estadísticas', {
            'fields': ('total_horarios', 'accesos_hoy', 'accesos_semana'),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Estado', ordering='estado')
    def estado_badge(self, obj):
        if obj.estado:
            return format_html('<span style="color: green; font-weight: bold;">✓ Activo</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Inactivo</span>')
    
    @admin.display(description='Horarios')
    def total_horarios(self, obj):
        return obj.horarios.count()
    
    @admin.display(description='Accesos Hoy')
    def accesos_hoy(self, obj):
        hoy = timezone.now().date()
        total = obj.registros_acceso.filter(fecha_hora__date=hoy).count()
        permitidos = obj.registros_acceso.filter(fecha_hora__date=hoy, acceso_permitido=True).count()
        return format_html('<strong>{}</strong> total ({} permitidos)', total, permitidos)
    
    @admin.display(description='Accesos esta Semana')
    def accesos_semana(self, obj):
        hace_7_dias = timezone.now() - timedelta(days=7)
        return obj.registros_acceso.filter(fecha_hora__gte=hace_7_dias).count()


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ['docente', 'laboratorio', 'dia_semana', 'hora_inicio', 'hora_fin', 'duracion']
    list_filter = ['dia_semana', 'laboratorio', 'created_at']
    search_fields = ['docente__nombres', 'laboratorio__nombre']
    ordering = ['dia_semana', 'hora_inicio']
    readonly_fields = ['created_at', 'updated_at', 'duracion']
    autocomplete_fields = ['docente', 'laboratorio']
    
    fieldsets = (
        ('Asignación', {
            'fields': ('docente', 'laboratorio')
        }),
        ('Horario', {
            'fields': ('dia_semana', 'hora_inicio', 'hora_fin', 'duracion')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Duración')
    def duracion(self, obj):
        if obj.hora_inicio and obj.hora_fin:
            inicio = timezone.datetime.combine(timezone.now().date(), obj.hora_inicio)
            fin = timezone.datetime.combine(timezone.now().date(), obj.hora_fin)
            duracion = fin - inicio
            horas = duracion.seconds // 3600
            minutos = (duracion.seconds % 3600) // 60
            return f'{horas}h {minutos}min'
        return '-'


@admin.register(RegistroAcceso)
class RegistroAccesoAdmin(admin.ModelAdmin):
    list_display = ['fecha_hora', 'docente', 'laboratorio', 'estado_acceso', 'motivo']
    list_filter = ['acceso_permitido', 'fecha_hora', 'laboratorio', 'docente']
    search_fields = ['docente__nombres', 'docente__codigo_docente', 'laboratorio__nombre', 'motivo']
    ordering = ['-fecha_hora']
    readonly_fields = ['fecha_hora']
    autocomplete_fields = ['docente', 'laboratorio']
    date_hierarchy = 'fecha_hora'
    
    list_per_page = 50
    
    fieldsets = (
        ('Información del Acceso', {
            'fields': ('docente', 'laboratorio', 'fecha_hora')
        }),
        ('Resultado', {
            'fields': ('acceso_permitido', 'motivo')
        }),
    )
    
    @admin.display(description='Estado', ordering='acceso_permitido')
    def estado_acceso(self, obj):
        if obj.acceso_permitido:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-weight: bold;">✓ PERMITIDO</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">✗ DENEGADO</span>'
        )
    
    def has_add_permission(self, request):
        # Los registros solo se crean automáticamente
        return False
    
    def has_change_permission(self, request, obj=None):
        # Los registros no se pueden modificar
        return False
