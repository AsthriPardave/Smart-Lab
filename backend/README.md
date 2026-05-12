# SmartLab Backend

Backend del proyecto SmartLab desarrollado con Django y Django REST Framework. Sistema de control de acceso a laboratorios mediante registro de huellas dactilares y gestión de horarios.

## Características

- API RESTful completa con Django REST Framework
- Base de datos PostgreSQL
- Sistema de control de acceso por biometría
- Gestión de horarios y laboratorios
- Registro detallado de accesos
- Panel de administración de Django
- Dockerizado para fácil despliegue
- Filtros, búsqueda y paginación en todos los endpoints

## Modelos de Base de Datos

### Docente
Información de los docentes que tienen acceso a los laboratorios.
- **Campos**: nombres, correo, código_docente, activo, fingerprint
- **Relaciones**: Múltiples horarios y registros de acceso

### Dispositivo
Dispositivos de control de acceso (lectores de huella digital).
- **Campos**: código, IP, estado
- **Relaciones**: Un laboratorio

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
- **Índices**: Optimizado para consultas por fecha y estado

## Requisitos

- Docker
- Docker Compose

## Instalación

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
├── api/                 # App principal de la API
│   ├── views.py         # Vistas de la API
│   ├── models.py        # Modelos de datos
│   ├── urls.py          # URLs de la API
│   └── ...
├── manage.py            # Script de gestión de Django
├── requirements.txt     # Dependencias de Python
├── Dockerfile           # Configuración de Docker
├── docker-compose.yml   # Orquestación de contenedores
└── .env                 # Variables de entorno (no versionado)
```

## Endpoints

### API Principal
La API está disponible en `http://localhost:8000/api/`

#### Recursos disponibles:
- `/api/docentes/` - Gestión de docentes
- `/api/dispositivos/` - Gestión de dispositivos biométricos
- `/api/laboratorios/` - Gestión de laboratorios
- `/api/horarios/` - Gestión de horarios de acceso
- `/api/registros-acceso/` - Registro de accesos

#### Endpoints especiales:
- `/api/health/` - Health check de la API
- `/api/docentes/activos/` - Lista solo docentes activos
- `/api/docentes/{id}/horarios/` - Horarios de un docente
- `/api/laboratorios/disponibles/` - Lista laboratorios activos
- `/api/laboratorios/{id}/horarios/` - Horarios de un laboratorio
- `/api/horarios/por_dia/?dia=Lunes` - Horarios filtrados por día
- `/api/registros-acceso/recientes/` - Últimos 50 registros
- `/api/registros-acceso/por_fecha/?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD` - Registros por rango de fechas

### Panel de Administración
- **URL:** `http://localhost:8000/admin/`
- **Descripción:** Panel de administración de Django con interfaz gráfica

## Tecnologías

- **Django 5.0.4** - Framework web
- **Django REST Framework** - Para crear APIs RESTful
- **PostgreSQL 15** - Base de datos
- **Docker** - Containerización
- **JWT** - Autenticación

## Desarrollo

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
