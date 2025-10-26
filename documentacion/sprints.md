# 🧩 Proyecto: Punto PYMES  
## Sistema de Control de Personal  
**Stack:** Django · Django REST Framework · HTMX · Bootstrap · PostgreSQL

---

## 🗓️ SPRINT 0 — Semana 1  
### Objetivo: Arranque técnico
**Meta:** Entorno listo, repositorio estructurado y primeras pruebas con las tecnologías.

#### 🧠 Tareas principales
- Configurar repositorio (GitHub/GitLab) y flujo de ramas (`main`, `dev`, `feature/*`).
- Crear entorno de desarrollo (Python, Django, Django REST framework, HTMX, Bootstrap y PostgreSQL).
- Instalar Django, DRF, HTMX y Bootstrap.
- Configurar el entorno de desarrollo.
- Probar endpoints básicos (`/api/ping/`) y página inicial con HTMX.
- Despliegue “Hello World” en un servidor.

#### 🎯 Entregables
- Proyecto base ejecutándose.  
- Documentación de instalación en README.  

---

## 🗓️ SPRINT 1 — Semana 2  
### Objetivo: Investigaciones de aprendizaje y diseño funcional  
**Meta:** Comprender el dominio y definir contratos de integración.

#### 🧠 Tareas principales
- Diseñar modelo de datos preliminar y diagramas entidad-relación.  
- Crear documentación para API v1.  
- Investigación de conexión con página antigua (endpoint de prueba).  
- Investigación de API para futura app móvil.

#### 🎯 Entregables
- Documento API v1.  
- Diagrama de base de datos.  
- Diagrama definido con conexión a app móvil.

---

## 🗓️ SPRINT 2 — Semanas 3–4  
### Objetivo: Módulo de Empleados + Autenticación/Roles  
**Meta:** CRUD completo y control de acceso por rol.

#### 🧠 Tareas principales
- Modelo `User` y `Employee`.
- Implementar login/logout y permisos (Admin, RRHH, Supervisor, Empleado).  
- CRUD de empleados (formularios modales con HTMX + Bootstrap).  
- Endpoints REST: `/api/v1/employees/` y `/api/v1/employees/{id}`.  
- Validaciones y control de permisos en DRF.  

#### 🎯 Entregables
- Gestión de empleados funcional (UI + API).  
- Roles activos y permisos validados.  
- Tests básicos y documentación actualizada.

---

## 🗓️ SPRINT 3 — Semanas 5–6  
### Objetivo: Asistencia y Control de Horarios  
**Meta:** Registrar, consultar y reportar horas de trabajo.

#### 🧠 Tareas principales
- Modelo `Attendance` (empleado, fecha, hora_entrada, hora_salida, total_horas).  
- Formulario de registro y listado (filtros HTMX).  
- API `/api/v1/attendance/` con paginación y filtros por rango de fechas.  
- Exportación CSV de registros de asistencia.  

#### 🎯 Entregables
- Módulo de asistencia operativo.  
- API estable para futuras integraciones.  
- Reporte CSV descargable.

---

## 🗓️ SPRINT 4 — Semanas 7–8  
### Objetivo: Permisos, Vacaciones y Horas Extras  
**Meta:** Crear workflows simples de solicitud y aprobación.

#### 🧠 Tareas principales
- Modelos `LeaveRequest` y `Overtime`.  
- Vistas: solicitudes (Empleado) y aprobaciones (Supervisor/RRHH).  
- API `/api/v1/leaves/` y `/api/v1/overtime/`.  
- Validaciones de saldo anual y solapamientos.  
- Notificación visual (banner o tabla actualizable con HTMX).  

#### 🎯 Entregables
- Flujo completo de permisos/vacaciones/horas extra.  
- Endpoints REST documentados y probados.  
- Pruebas de reglas de negocio.

---

## 🗓️ SPRINT 5 — Semanas 9–10  
### Objetivo: POA Anual y Dashboard de Reportes  
**Meta:** Registrar actividades/tareas y mostrar indicadores clave.

#### 🧠 Tareas principales
- Modelos `POAActivity` y `POATask`.  
- CRUD con filtrado y edición rápida (HTMX).  
- API `/api/v1/poa/activities`, `/api/v1/poa/tasks`, `/api/v1/kpis`.  
- Dashboard con KPIs: empleados activos, ausencias, horas extra, avance POA.  
- Exportación CSV de reportes por módulo.  

#### 🎯 Entregables
- Módulo POA funcional.  
- Dashboard con widgets y métricas.  
- API KPIs lista para consumo externo.

---

## 🗓️ SPRINT 6 — Semanas 11–12  
### Objetivo: Pulido, Seguridad y Despliegue final  
**Meta:** Entregar un MVP estable, seguro y desplegado en producción.

#### 🧠 Tareas principales
- Revisar permisos, CSRF, CORS, JWT, paginación y validaciones.   
- Preparar `API v1` final y colección Postman.  
- Población base de datos demo (usuarios, roles, empleados).  
- Despliegue en producción con backups.  
- Prueba de demo funcional.

#### 🎯 Entregables
- Sistema completo desplegado.  
- Documentación final (instalación, uso y API).  
- Demo operativa y usuarios de prueba.

---

## ✅ Resumen de Entregables Totales

| Sprint | Entregable Principal | Estado Esperado |
|:-------|:---------------------|:----------------|
| 0 | Proyecto base + API + Continuos Integration | 🟢 |
| 1 | Modelo de datos + API inicial | 🟢 |
| 2 | Módulo de empleados + Roles | 🟢 |
| 3 | Control de asistencia | 🟢 |
| 4 | Permisos, vacaciones y horas extra | 🟢 |
| 5 | POA + Dashboard + KPIs | 🟢 |
| 6 | Despliegue y documentación final | 🟢 |
