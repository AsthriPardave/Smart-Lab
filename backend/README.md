# SmartLab Backend

Backend del proyecto SmartLab desarrollado con Django. Sistema de control de acceso a laboratorios mediante registro de huellas dactilares y gestión de horarios.

## 🎯 Arquitectura

Este proyecto utiliza **Django Admin con Jazzmin** como interfaz principal de gestión. No incluye una API REST completa, solo un endpoint específico para la validación de accesos biométricos.

### Componentes:

- **Panel de Administración (Django Admin + Jazzmin)**: Interfaz visual para gestionar docentes, laboratorios, dispositivos, horarios y ver registros de acceso
- **API Biométrica**: Un único endpoint POST para validar accesos desde dispositivos lectores de huella
- **Base de datos PostgreSQL**: Almacenamiento de datos
- **Docker**: Contenedorización completa del sistema

## 📋 Características

- ✅ Panel administrativo mejorado con Jazzmin (interfaz moderna y amigable)
- ✅ Gestión completa de docentes, laboratorios y dispositivos
- ✅ Asignación de horarios por docente y laboratorio
- ✅ Validación automática de accesos biométricos
- ✅ Registro detallado de todos los intentos de acceso
- ✅ Estadísticas en tiempo real (accesos del día, semana, etc.)
- ✅ Búsqueda, filtros y ordenamiento avanzado
- ✅ Dockerizado para fácil despliegue

## 🗂️ Modelos de Base de Datos

### Docente
Información de los docentes que tienen acceso a los laboratorios.
- **Campos**: nombres, correo, código_docente, activo, fingerprint
- **Relaciones**: Múltiples horarios y registros de acceso

### Dispositivo
Dispositivos de control de acceso (lectores de huella digital).
- **Campos**: código, IP, estado
- **Relaciones**: Un laboratorio (OneToOne)

### Laboratorio
Espacios físicos controlados con acceso biométrico.
- **Campos**: nombre, ubicación, estado, dispositivo
- **Relaciones**: Múltiples horarios y registros de acceso

### Horario
Horarios autorizados de acceso para docentes a laboratorios específicos.
- **Campos**: día_semana, hora_inicio, hora_fin, docente, laboratorio
- **Validación**: La hora de inicio debe ser anterior a la hora de fin

### RegistroAcceso
Registro de todos los intentos de acceso (permitidos y denegados).
- **Campos**: fecha_hora, acceso_permitido, motivo, docente, laboratorio
- **Nota**: Los registros son de solo lectura desde el admin

## 🔌 Endpoint API

### POST `/api/validar-acceso/`

Endpoint para validar accesos desde dispositivos biométricos.

**Request:**
```json
{
    "fingerprint_id": 123,
    "dispositivo_codigo": "DISP001"
}
```

**Response exitosa (200):**
```json
{
    "acceso_permitido": true,
    "motivo": "Acceso autorizado",
    "docente": {
        "nombres": "Juan Pérez",
        "codigo": "DOC001",
        "correo": "juan@example.com"
    },
    "laboratorio": {
        "nombre": "Laboratorio 1",
        "ubicacion": "Piso 2"
    },
    "horario": {
        "dia": "Lunes",
        "hora_inicio": "08:00",
        "hora_fin": "10:00"
    },
    "registro_id": 123
}
```

**Response denegada (403):**
```json
{
    "acceso_permitido": false,
    "motivo": "Acceso denegado: fuera de horario autorizado",
    "docente": {
        "nombres": "Juan Pérez",
        "codigo": "DOC001"
    },
    "laboratorio": {
        "nombre": "Laboratorio 1"
    },
    "dia_hora": "Lunes 18:30",
    "registro_id": 124
}
```

### Otros Endpoints

- `GET /api/` - Información de la API
- `GET /api/health/` - Health check

## 🚀 Instalación y Despliegue

### Requisitos

- Docker
- Docker Compose

### 1. Clonar el repositorio

```bash
cd backend
```

### 2. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y ajusta las variables según sea necesario:

```bash
cp .env.example .env
```

### 3. Construir y levantar los contenedores

```bash
docker-compose up --build
```

Este comando:
- Construirá la imagen de Docker
- Levantará el contenedor de PostgreSQL
- Levantará el contenedor de Django
- Expondrá la aplicación en `http://localhost:8000`

### 4. Aplicar migraciones

En otra terminal, ejecuta:

```bash
docker-compose exec web python manage.py migrate
```

### 5. Crear superusuario (opcional)

```bash
docker-compose exec web python manage.py createsuperuser
```

## Comandos útiles

### Detener los contenedores
```bash
docker-compose down
```

### Ver logs
```bash
docker-compose logs -f
```

### Ejecutar comandos de Django
```bash
docker-compose exec web python manage.py <comando>
```

### Acceder al shell de Django
```bash
docker-compose exec web python manage.py shell
```

### Crear una nueva app
```bash
docker-compose exec web python manage.py startapp nombre_app
```

## Estructura del Proyecto

```
backend/
├── config/              # Configuración del proyecto
│   ├── settings.py      # Configuración de Django
│   ├── urls.py          # URLs principales
│   ├── wsgi.py          # WSGI config
│   └── asgi.py          # ASGI config
├── api/                 # App principal
│   ├── views.py         # Vistas y endpoint biométrico
│   ├── models.py        # Modelos de datos
│   ├── admin.py         # Configuración del panel admin
│   ├── urls.py          # URLs de la API
│   └── migrations/      # Migraciones de base de datos
├── manage.py            # Script de gestión de Django
├── requirements.txt     # Dependencias de Python
├── Dockerfile           # Configuración de Docker
├── docker-compose.yml   # Orquestación de contenedores
└── .env                 # Variables de entorno (no versionado)
```

## 🎨 Panel de Administración (Principal)

**URL:** `http://localhost:8000/admin/`

El panel administrativo es la interfaz principal del sistema, mejorado con Jazzmin para una experiencia moderna y amigable.

### Funcionalidades:

#### 📚 Gestión de Docentes
- Crear, editar, buscar docentes
- Activar/desactivar docentes masivamente
- Ver estadísticas de accesos
- Badges de estado visual
- Búsqueda por nombre, correo, código

#### 🔬 Gestión de Laboratorios
- Administrar laboratorios y ubicaciones
- Asignar dispositivos biométricos
- Ver estadísticas de accesos del día y semana
- Filtros por estado

#### 🖥️ Gestión de Dispositivos
- Registrar lectores de huella
- Configurar IPs de dispositivos
- Asignar a laboratorios
- Control de estado activo/inactivo

#### 📅 Gestión de Horarios
- Asignar horarios por docente y laboratorio
- Validación automática de rangos horarios
- Filtros por día de la semana
- Autocomplete para facilitar asignaciones

#### 📊 Registros de Acceso
- Visualización completa de accesos
- Filtros por fecha, laboratorio, estado
- Badges visuales de permitido/denegado
- Solo lectura (se crean automáticamente)
- Jerarquía por fecha para navegación

## 🔌 API Biométrica

### Panel de Administración
- **URL:** `http://localhost:8000/admin/`
- **Descripción:** Panel de administración de Django mejorado con Jazzmin

## 💻 Tecnologías

- **Django 5.0.4** - Framework web
- **Django Jazzmin** - Panel administrativo moderno
- **PostgreSQL 15** - Base de datos
- **Docker** - Containerización
- **Python 3.11+** - Lenguaje de programación

## 🛠️ Desarrollo

### Modo desarrollo

El proyecto está configurado para desarrollo con hot-reload. Los cambios en el código se reflejarán automáticamente.

### Testing

```bash
docker-compose exec web python manage.py test
```

## Producción

Para producción, asegúrate de:
1. Cambiar `DEBUG=False` en el archivo `.env`
2. Generar una nueva `SECRET_KEY`
3. Configurar `ALLOWED_HOSTS` apropiadamente
4. Usar un servidor WSGI como Gunicorn
5. Configurar un servidor web como Nginx
