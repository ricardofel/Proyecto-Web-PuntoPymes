
# 🟠 PuntoPymes

### Plataforma Web Modular para la Gestión del Talento Humano en PYMES

**PuntoPymes** es una plataforma web desarrollada en **Django** orientada a la gestión integral del talento humano en pequeñas y medianas empresas.
El sistema centraliza información organizacional, control básico de asistencia, solicitudes internas y planificación anual, bajo una **arquitectura modular, escalable y mantenible**.

El proyecto forma parte del **Reto PuntoPymes – UTPL** y está diseñado siguiendo buenas prácticas de ingeniería de software, separación de responsabilidades y extensibilidad futura mediante una **API REST**.

---

## 🎯 Objetivo del proyecto

Diseñar e implementar una solución web que permita a las PYMES:

- Organizar su estructura empresarial y su personal.
- Registrar y consultar eventos básicos de asistencia.
- Gestionar solicitudes internas (permisos, vacaciones, ausencias).
- Definir indicadores (KPIs) y planes operativos anuales (POA).
- Mantener trazabilidad de acciones mediante auditoría.
- Exponer datos a sistemas externos a través de una API REST.

---

## ⚙️ Tecnologías utilizadas

- **Backend:** Django, Django REST Framework
- **Frontend:** HTMX, Tailwind CSS
- **Base de datos:** PostgreSQL
- **Arquitectura:** Modular por aplicaciones Django
- **Control de versiones:** Git

---

## ⭐ Características principales

- Gestión de empresas y estructura organizacional.
- Administración de usuarios, roles y permisos.
- Fichas laborales de empleados.
- Registro web de eventos de asistencia.
- Solicitudes de permisos, vacaciones y ausencias.
- Definición y cálculo de KPIs.
- Plan Operativo Anual (POA) por objetivos y actividades.
- Sistema de auditoría de acciones.
- API REST para integraciones externas.
- Arquitectura limpia y escalable.

---

## 🧩 Módulos del sistema

| Módulo                  | Descripción                                          |
| ------------------------ | ----------------------------------------------------- |
| **core**           | Empresas, unidades organizacionales, puestos y turnos |
| **usuarios**       | Autenticación, roles y permisos                      |
| **empleados**      | Ficha laboral y estado                                |
| **asistencia**     | Registro de eventos de asistencia                     |
| **solicitudes**    | Permisos, vacaciones y ausencias                      |
| **kpi**            | Indicadores de gestión                               |
| **poa**            | Objetivos, metas y actividades                        |
| **notificaciones** | Alertas internas                                      |
| **integraciones**  | Webhooks e integraciones externas                     |
| **auditoria**      | Registro de acciones del sistema                      |

---

## 🗂️ Estructura del proyecto

```
source/
├── core/
├── usuarios/
├── empleados/
├── asistencia/
├── solicitudes/
├── kpi/
├── poa/
├── notificaciones/
├── integraciones/
├── auditoria/
├── talenttrack/
├── manage.py
├── requirements.txt
└── venv/
```

Cada app contiene:

```
api/
views/
services/
templates/
models.py
urls.py
tests/
```

---

## 🗄️ Base de datos (PostgreSQL)

```sql
CREATE DATABASE puntopymes;
```

Variables de entorno:

```env
DB_NAME=puntopymes
DB_USER=puntopymes_user
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```

---

## 🚀 Ejecución en desarrollo

```bash
git clone <url-del-repositorio>
cd Proyecto-Web-PuntoPymes/source
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 📘 Documentación técnica

Consultar:

```
docs/Arquitectura_Estructura_TalentTrack.md
```

---

## 📌 Estado del proyecto

🔧 En desarrollo
🎓 Proyecto académico – UTPL
