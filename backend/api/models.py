from django.db import models
from django.core.validators import validate_ipv4_address


class Docente(models.Model):
    """
    Modelo para almacenar información de los docentes
    """
    nombres = models.CharField(max_length=100, verbose_name="Nombres completos")
    correo = models.EmailField(max_length=150, unique=True, verbose_name="Correo electrónico")
    codigo_docente = models.CharField(max_length=10, unique=True, verbose_name="Código de docente")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fingerprint = models.IntegerField(unique=True, verbose_name="ID de huella digital")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'docente'
        verbose_name = 'Docente'
        verbose_name_plural = 'Docentes'
        ordering = ['nombres']
    
    def __str__(self):
        return f"{self.nombres} ({self.codigo_docente})"


class Dispositivo(models.Model):
    """
    Modelo para dispositivos de control de acceso (lectores de huella)
    """
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código del dispositivo")
    ip = models.CharField(
        max_length=50, 
        validators=[validate_ipv4_address],
        verbose_name="Dirección IP"
    )
    estado = models.BooleanField(default=True, verbose_name="Estado activo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dispositivo'
        verbose_name = 'Dispositivo'
        verbose_name_plural = 'Dispositivos'
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.ip}"


class Laboratorio(models.Model):
    """
    Modelo para laboratorios
    """
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del laboratorio")
    ubicacion = models.CharField(max_length=50, verbose_name="Ubicación")
    estado = models.BooleanField(default=True, verbose_name="Estado activo")
    dispositivo = models.OneToOneField(
        Dispositivo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='laboratorio',
        verbose_name="Dispositivo asociado"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'laboratorio'
        verbose_name = 'Laboratorio'
        verbose_name_plural = 'Laboratorios'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.ubicacion}"


class Horario(models.Model):
    """
    Modelo para horarios de acceso de docentes a laboratorios
    """
    DIAS_SEMANA = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]
    
    dia_semana = models.CharField(max_length=15, choices=DIAS_SEMANA, verbose_name="Día de la semana")
    hora_inicio = models.TimeField(verbose_name="Hora de inicio")
    hora_fin = models.TimeField(verbose_name="Hora de fin")
    docente = models.ForeignKey(
        Docente,
        on_delete=models.CASCADE,
        related_name='horarios',
        verbose_name="Docente"
    )
    laboratorio = models.ForeignKey(
        Laboratorio,
        on_delete=models.CASCADE,
        related_name='horarios',
        verbose_name="Laboratorio"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'horario'
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = [['docente', 'laboratorio', 'dia_semana', 'hora_inicio']]
    
    def __str__(self):
        return f"{self.docente.nombres} - {self.laboratorio.nombre} ({self.dia_semana} {self.hora_inicio}-{self.hora_fin})"


class RegistroAcceso(models.Model):
    """
    Modelo para registrar intentos de acceso al laboratorio
    """
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    acceso_permitido = models.BooleanField(verbose_name="Acceso permitido")
    motivo = models.CharField(max_length=200, verbose_name="Motivo", blank=True)
    docente = models.ForeignKey(
        Docente,
        on_delete=models.CASCADE,
        related_name='registros_acceso',
        verbose_name="Docente"
    )
    laboratorio = models.ForeignKey(
        Laboratorio,
        on_delete=models.CASCADE,
        related_name='registros_acceso',
        verbose_name="Laboratorio"
    )
    
    class Meta:
        db_table = 'registro_acceso'
        verbose_name = 'Registro de Acceso'
        verbose_name_plural = 'Registros de Acceso'
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['-fecha_hora']),
            models.Index(fields=['acceso_permitido']),
        ]
    
    def __str__(self):
        estado = "Permitido" if self.acceso_permitido else "Denegado"
        return f"{self.docente.nombres} - {self.laboratorio.nombre} ({estado}) - {self.fecha_hora}"
