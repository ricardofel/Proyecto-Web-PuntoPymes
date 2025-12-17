# 📄 Documentación Técnica – Talent Track 2.0

**Sistema de Gestión de Personal**
**Integrantes:** Ricardo Fabian Espinosa Largo, Juan Diego Guerrero Camargo y Pedro Sebastian Yepez Iñiguez

---

# 1. Resumen del Proyecto

Talent Track 2.0 es una plataforma web orientada a la **Gestión de Talento Humano**, diseñada para empresas que requieren controlar y administrar información clave del personal. El sistema integra:

- **Administración de usuarios y roles**
- **Gestión de solicitudes (permisos, vacaciones, atrasos)**
- **Registro básico de asistencia**
- **KPIs simples**
- **Actividades del POA**

---

# 2. Justificación del Proyecto

Las organizaciones necesitan hoy sistemas centralizados que permitan:

- Registrar de forma confiable la asistencia laboral
- Automatizar solicitudes de permisos
- Administrar usuarios con diferentes niveles de acceso
- Monitorear indicadores básicos de desempeño
- Planificar actividades para el cumplimiento de objetivos

Talent Track 2.0 responde a esta necesidad de forma modular, con un enfoque multiempresa, permitiendo que una sola plataforma gestione varias compañías con roles diferenciados.

Este enfoque es ideal para empresas medianas-grandes y para consultoras que manejan varios clientes.

---

# 3. Arquitectura del Sistema

La arquitectura final sigue un modelo cliente-servidordesacoplado, pero evita la complejidad innecesaria de una SPA y se enfoca en simplicidad + escalabilidad real.

## 3.1. Frontend – HTMX + Tailwind CSS

Se eligió **HTMX** por las siguientes razones:

- Permite interactividad sin usar frameworks pesados (React/Vue).
- Facilita partial rendering y peticiones dinámicas desde HTML.
- Reduce drásticamente la complejidad del frontend, pero mantiene UX moderna.

**Tailwind CSS** permite:

- Estilo consistente y limpio.
- Rapidez al construir vistas.
- Minimizar archivos CSS gracias a purge en producción.
- Adaptabilidad a móviles sin esfuerzo extra.

---

## 3.2. Backend – Django + Django REST Framework

**Django** se usa como núcleo de reglas de negocio:

- Sistema de usuarios.
- Validaciones.
- Roles y permisos.
- Renderización de vistas con HTMX.
- Seguridad y autenticación.

**Django REST Framework (DRF)** se usa para:

- Endpoints REST del sistema.
- Intercambio JSON.
- Permisos por rol.
- Serialización de datos.
- Comunicación con el frontend HTMX cuando corresponde.

---

## 3.3. Base de Datos – PostgreSQL

Se seleccionó **PostgreSQL** por:

- Fiabilidad en producción.
- Soporte para transacciones ACID.
- Tipos JSONB para datos dinámicos.
- Excelente rendimiento con Django.
- Ideal para sistemas multiempresa.

---

## 3.4. Control de Versiones

- Git + GitHub.
- Uso de ramas para nuevas funcionalidades.
- `.gitignore` configurado para venv, migraciones, estáticos, etc.

---

# 4. Módulos Funcionales

Se estableció la estructura final:

---

## 4.1. Módulo de Usuario (Roles y Permisos)

### Funcionalidad:

- Login y logout
- CRUD básico de usuarios
- Asignación de roles

  - SuperAdmin
  - Admin RRHH
  - Manager
  - Empleado

---

## 4.2. Módulo de Solicitudes

### Funcionalidad:

- Empleado crea solicitud
- Manager o Admin aprueban/rechazan
- Historial de solicitudes
- Notificaciones internas simples

---

## 4.3. Módulo de Asistencia (Básico)

### Funcionalidad:

- Iniciar jornada (check-in)
- Finalizar jornada (check-out)
- Visualizar historial
- Ajustar horas

---

## 4.4. Módulo de KPIs

### Funcionalidad:

- KPIs simples desde asistencia
- Visualización en tablas

---

## 4.5. Módulo de POA / Actividades – Opcional

### Funcionalidad:

- Crear actividades
- Actualizar progreso
- Asignar responsables

---

# 6. Relación con Diagramas UML

- Casos de Uso
- Contexto
- Actividades
- Secuencias
- Diagrama de Clases (basado en la BD oficial)

---

# 7. Conclusión

El nuevo diseño de Talent Track 2.0 refleja un sistema profesional, escalable y modular.
Se enfoca en lo esencial, pero con arquitectura realista y tecnologías modernas: **Django + DRF + HTMX + Tailwind + PostgreSQL**.
