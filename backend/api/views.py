from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime
import json

from .models import Docente, Dispositivo, Laboratorio, Horario, RegistroAcceso


def index(request):
    """
    Vista principal de la API
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'SmartLab API - Sistema de Control de Acceso Biométrico',
        'version': '2.0',
        'endpoints': {
            'validar_acceso': '/api/validar-acceso/ [POST]',
            'health': '/api/health/ [GET]'
        }
    })


def health_check(request):
    """
    Endpoint para verificar el estado de la API
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'SmartLab API is running',
        'timestamp': timezone.now().isoformat()
    })


@csrf_exempt
@require_http_methods(["POST"])
def validar_acceso(request):
    """
    Endpoint principal para validar acceso biométrico
    
    Recibe:
    {
        "fingerprint_id": 123,
        "dispositivo_codigo": "DISP001"
    }
    
    Retorna:
    {
        "acceso_permitido": true/false,
        "motivo": "mensaje",
        "docente": {...},
        "laboratorio": {...}
    }
    """
    try:
        # Parsear datos del request
        data = json.loads(request.body)
        fingerprint_id = data.get('fingerprint_id')
        dispositivo_codigo = data.get('dispositivo_codigo')
        
        # Validar datos requeridos
        if not fingerprint_id or not dispositivo_codigo:
            return JsonResponse({
                'acceso_permitido': False,
                'motivo': 'Datos incompletos: se requiere fingerprint_id y dispositivo_codigo'
            }, status=400)
        
        # Buscar dispositivo
        try:
            dispositivo = Dispositivo.objects.get(codigo=dispositivo_codigo, estado=True)
        except Dispositivo.DoesNotExist:
            return JsonResponse({
                'acceso_permitido': False,
                'motivo': f'Dispositivo {dispositivo_codigo} no encontrado o inactivo'
            }, status=404)
        
        # Verificar que el dispositivo esté asociado a un laboratorio
        try:
            laboratorio = dispositivo.laboratorio
            if not laboratorio.estado:
                return JsonResponse({
                    'acceso_permitido': False,
                    'motivo': f'Laboratorio {laboratorio.nombre} está inactivo'
                }, status=403)
        except Laboratorio.DoesNotExist:
            return JsonResponse({
                'acceso_permitido': False,
                'motivo': f'Dispositivo {dispositivo_codigo} no está asociado a ningún laboratorio'
            }, status=404)
        
        # Buscar docente por huella
        try:
            docente = Docente.objects.get(fingerprint=fingerprint_id, activo=True)
        except Docente.DoesNotExist:
            # Registrar intento fallido
            RegistroAcceso.objects.create(
                docente=None,
                laboratorio=laboratorio,
                acceso_permitido=False,
                motivo=f'Huella digital {fingerprint_id} no registrada o docente inactivo'
            )
            return JsonResponse({
                'acceso_permitido': False,
                'motivo': 'Huella digital no registrada o docente inactivo'
            }, status=403)
        
        # Validar horario autorizado
        #ahora = timezone.now()
        ahora = timezone.timezone()
        dia_actual = ahora.strftime('%A')  # Nombre del día en inglés
        hora_actual = ahora.time()
        
        # Mapeo de días en inglés a español
        dias_map = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miércoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        dia_espanol = dias_map.get(dia_actual, dia_actual)
        
        # Buscar horario autorizado
        horario_valido = Horario.objects.filter(
            docente=docente,
            laboratorio=laboratorio,
            dia_semana=dia_espanol,
            hora_inicio__lte=hora_actual,
            hora_fin__gte=hora_actual
        ).first()
        
        if horario_valido:
            # Acceso permitido
            registro = RegistroAcceso.objects.create(
                docente=docente,
                laboratorio=laboratorio,
                acceso_permitido=True,
                motivo='Acceso autorizado'
            )
            
            return JsonResponse({
                'acceso_permitido': True,
                'motivo': 'Acceso autorizado',
                'docente': {
                    'nombres': docente.nombres,
                    'codigo': docente.codigo_docente,
                    'correo': docente.correo
                },
                'laboratorio': {
                    'nombre': laboratorio.nombre,
                    'ubicacion': laboratorio.ubicacion
                },
                'horario': {
                    'dia': dia_espanol,
                    'hora_inicio': horario_valido.hora_inicio.strftime('%H:%M'),
                    'hora_fin': horario_valido.hora_fin.strftime('%H:%M')
                },
                'registro_id': registro.id
            }, status=200)
        else:
            # Acceso denegado por horario
            registro = RegistroAcceso.objects.create(
                docente=docente,
                laboratorio=laboratorio,
                acceso_permitido=False,
                motivo=f'Fuera de horario autorizado ({dia_espanol} {hora_actual.strftime("%H:%M")})'
            )
            
            return JsonResponse({
                'acceso_permitido': False,
                'motivo': f'Acceso denegado: fuera de horario autorizado',
                'docente': {
                    'nombres': docente.nombres,
                    'codigo': docente.codigo_docente
                },
                'laboratorio': {
                    'nombre': laboratorio.nombre
                },
                'dia_hora': f'{dia_espanol} {hora_actual.strftime("%H:%M")}',
                'registro_id': registro.id
            }, status=403)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'acceso_permitido': False,
            'motivo': 'Error en formato JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'acceso_permitido': False,
            'motivo': f'Error interno: {str(e)}'
        }, status=500)


# Miau miau miau miau miau miau
@csrf_exempt
@require_http_methods(["POST"])
def registrar_docente_demo(request):
    try:
        data = json.loads(request.body)
        fingerprint_id = data.get('fingerprint_id')

        if not fingerprint_id:
            return JsonResponse({'status': 'error', 'message': 'fingerprint_id requerido'}, status=400)

        # Usamos update_or_create para que si el ID de huella vuelve a registrarse, 
        # no rompa la base de datos por duplicados únicos, sino que lo actualice.
        docente, created = Docente.objects.update_or_create(
            fingerprint=fingerprint_id,
            defaults={
                'nombres': f'Docente Demo {fingerprint_id}',
                'correo': f'docente_{fingerprint_id}_{int(timezone.now().timestamp())}@demo.com', # Correo único con timestamp
                'codigo_docente': f'DM{fingerprint_id:03d}', # Formato DM001, DM002
                'activo': True
            }
        )

        # Asegurar horario 24/7 para la demo
        laboratorio = Laboratorio.objects.filter(estado=True).first()
        if laboratorio:
            dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            for dia in dias:
                Horario.objects.get_or_create(
                    docente=docente,
                    laboratorio=laboratorio,
                    dia_semana=dia,
                    defaults={
                        'hora_inicio': '00:00',
                        'hora_fin': '23:59'
                    }
                )

        return JsonResponse({'status': 'ok', 'message': f'Docente {fingerprint_id} procesado correctamente.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)