# 🟠 PuntoPymes – Sistema de Control de Personal

PuntoPymes es una plataforma web modular para la gestión integral del talento humano en pequeñas y medianas empresas. Centraliza la información del personal, estructura organizacional, asistencia, permisos y planificación anual. Incluye una API REST que permite integrar el sistema con aplicaciones móviles o sistemas externos.

Desarrollado con **Django**, **Django REST Framework**, **HTMX**, **Tailwind CSS** y **PostgreSQL** como parte del **Reto PuntoPymes – UTPL**.

---

## ⭐ Características principales

- Gestión de empleados, contratos y estructura organizacional.
- Registro de asistencia web y móvil con validación por **GPS**.
- Solicitudes de permisos, vacaciones y ausencias.
- Generación de jornadas y control básico de horas trabajadas.
- Administración de roles y permisos internos.
- API REST completa para integraciones externas.
- Arquitectura modular, escalable y organizada.

---

## 🧩 Módulos incluidos

- **Core:** empresas, unidades organizacionales, puestos, turnos.
- **Usuarios:** credenciales, roles y asignación de permisos.
- **Empleados:** ficha laboral, contratos, documentos.
- **Asistencia:** marcaciones, geocercas, jornadas.
- **Solicitudes:** permisos, vacaciones, aprobaciones.
- **KPI:** definición y resultados de indicadores.
- **POA:** objetivos, metas y actividades por empleado.
- **Notificaciones:** alertas internas y externas.
- **Integraciones:** webhooks, ERP, exportación de nómina.
- **Auditoría:** registro de acciones del sistema.

---

# 🗄️ Crear la base de datos en PostgreSQL

Antes de ejecutar las migraciones, debes crear la base de datos manualmente.

1. Abrir PostgreSQL (psql, PgAdmin o similar).
2. Ejecutar:

```sql
CREATE DATABASE puntopymes;
```

Opcionalmente, crear el usuario:

```sql
CREATE USER puntopymes_user WITH PASSWORD 'tu_contraseña';
GRANT ALL PRIVILEGES ON DATABASE puntopymes TO puntopymes_user;
```

3. Configurar `.env`:

```
DB_NAME=puntopymes
DB_USER=puntopymes_user
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```

4. Ejecutar migraciones:

```bash
python manage.py migrate
```

---

# 🚀 Cómo ejecutar el proyecto (desarrollo)

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd Proyecto-Web-PuntoPymes/source
```

---

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv
.env\Scriptsctivate   # Windows
# o
source venv/bin/activate  # Linux/Mac
```

---

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

### 4. Crear archivo `.env`

```bash
cp .env.example .env
```

Completar valores en `.env`.

---

### 5. Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 6. Ejecutar servidor

```bash
python manage.py runserver
```

---

# 🏗️ Estructura del proyecto

```
source/
    core/
    empleados/
    usuarios/
    asistencia/
    solicitudes/
    notificaciones/
    integraciones/
    kpi/
    poa/
    auditoria/
    talenttrack/
    venv/
    manage.py
    requirements.txt
```

Cada app contiene:

```
api/          → serializers y viewsets
views/        → vistas web (HTMX)
services/     → lógica de negocio
templates/    → plantillas HTML
tests/        → pruebas unitarias
models.py     → modelos del módulo
urls.py       → rutas del módulo
```

---

# 📘 Documentación técnica

La documentación completa del proyecto se encuentra en:

```
docs/Arquitectura_Estructura_TalentTrack.md
```

Incluye:

- Arquitectura MVC extendida
- Estructura interna por app
- Contratos mínimos por módulo
- Relación con el diccionario de datos

---

# 🛠️ Flujo de trabajo (equipo)

1. Crear ramas por módulo:

```
feature/empleados-modelos
feature/asistencia-api
feature/solicitudes-vistas
```

2. Cada desarrollador trabaja dentro de su app.
3. Crear Pull Requests hacia `main`.
4. Código limpio, consistente y revisado.
