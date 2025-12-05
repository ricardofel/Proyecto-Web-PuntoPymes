# 📘 Arquitectura y Estructura del Proyecto Talent Track 2.0  
### *Documento Técnico de Organización – Versión Unificada*

---

## **1. Estructura General del Proyecto**

El sistema Talent Track 2.0 sigue una arquitectura modular basada en **Django + Django REST Framework + HTMX + TailwindCSS**, cumpliendo los requerimientos establecidos en:

- Documento técnico general del proyecto  
- Modelo de base de datos propuesto  
- Diccionario de datos Talent Track Multiempresa

La arquitectura se divide en **apps independientes**, cada una alineada a una parte funcional del sistema.

---

## **2. Lista Oficial de Apps del Proyecto**

Estas son las apps definitivas que debe contener el backend, 100% alineadas con el diccionario de datos.

---

### **1. `core`**
Modela las entidades base de la multiempresa.

Tablas incluidas:  
- empresa  
- unidad_organizacional  
- puesto  
- turno  

---

### **2. `empleados`**
Gestión del personal y su información contractual.

Tablas incluidas:  
- empleado  
- contrato  
- documento_empleado  

---

### **3. `usuarios`**
Autenticación, roles y permisos.

Tablas incluidas:  
- usuario  
- rol  
- usuario_rol  

---

### **4. `notificaciones`**
Sistema centralizado de alertas.

Tablas incluidas:  
- notificacion  
- notificacion_canal  

---

### **5. `asistencia`**
Registros de marcación y cálculo diario.

Tablas incluidas:  
- evento_asistencia  
- jornada_calculada  
- regla_asistencia  
- geocerca  
- dispositivo_empleado  

---

### **6. `solicitudes`**
Gestión de ausencias, permisos, vacaciones.

Tablas incluidas:  
- ausencia (catálogo de tipos)  
- solicitud_ausencia  
- aprobacion_ausencia  
- registro_vacaciones  

---

### **7. `kpi`**
Métricas y desempeño.

Tablas incluidas:  
- kpi  
- kpi_resultado  
*(Opcionales sugeridos)*  
- plantilla_kpi  
- asignacion_kpi  
- evaluacion_desempeno  

---

### **8. `poa`**
Planificación anual empresarial.

Tablas incluidas:  
- objetivo  
- objetivo_empleado  
- meta  
- meta_empleado  
- actividad  
- actividad_empleado  

---

### **9. `integraciones`**
Comunicación con sistemas externos.

Tablas incluidas:  
- reporte_programado  
- integracion_erp  
- webhook  
- exportacion_nomina  

---

### **10. `auditoria`** *(opcional pero recomendada)*
Tablas incluidas:  
- log_auditoria  

---

## **3. Estructura Interna de Cada App (Patrón M–C–V)**

Cada app seguirá la siguiente estructura base:

```
app_name/
├── __init__.py
├── apps.py
├── admin.py
│
├── models.py              # M – Model
│
├── views/                 # C – Controladores Web
│   ├── __init__.py
│   ├── entidad1_views.py
│   ├── entidad2_views.py
│   └── ...
│
├── services/              # C – Lógica de negocio
│   ├── __init__.py
│   └── servicios.py
│
├── api/                   # C – API REST
│   ├── __init__.py
│   ├── serializers.py
│   └── viewsets.py
│
├── templates/             # V – Presentación (HTMX + Tailwind)
│   └── app_name/
│       ├── lista.html
│       ├── formulario.html
│       └── ...
│
├── urls.py                # Rutas de la app
│
└── tests/                 # Pruebas unitarias y funcionales
    ├── __init__.py
    ├── test_models.py
    ├── test_views.py
    ├── test_services.py
    └── test_api.py
```

---

## **4. Rol de Cada Carpeta (Desglose Técnico)**

---

### **Model (M) → `models.py`**
Define las tablas y relaciones según el diccionario de datos:

Ejemplos:  
- Empresa  
- UnidadOrganizacional  
- Puesto  
- Turno  
- Empleado  
- Contrato  
- EventoAsistencia  
- KPI  
- Objetivo, Meta, Actividad  
- Etc.

---

### **Controller (C)**  
Distribuido en 3 carpetas, según responsabilidad:

#### **1. `views/` – Controladores Web (HTMX)**
- Manejan HTML dinámico  
- Renderizan plantillas  
- Responden a acciones vía HTMX  

#### **2. `services/` – Lógica de Negocio**
- Código reutilizable  
- Operaciones del dominio  
- Procesos internos del sistema  

#### **3. `api/` – API REST**
- Serialización  
- Endpoints REST  
- Conexión con ERPs externos  

---

### **View (V) → `templates/`**
HTML con HTMX + TailwindCSS.

Ejemplos:
```
templates/core/empresa_lista.html
templates/core/empresa_form.html
templates/core/turno_lista.html
```

---

## **5. Principios Clave de Diseño**

- **Multitenencia:** cada tabla lleva `empresa_id`.  
- **Modularidad:** apps independientes y autocontenidas.  
- **Controladores separados:** web (HTMX), API (REST), servicios.  
- **Alta mantenibilidad:** separación clara de capas.  
- **Escalabilidad real:** compatible con PostgreSQL y despliegue futuro.  

---

## **6. Relación con el Diccionario de Datos**

Toda la estructura presentada:

✔ Sigue exactamente los nombres de tablas  
✔ Mantiene los tipos de datos definidos  
✔ Respeta las relaciones 1–N, N–N y recursivas  
✔ Alinea las apps con los módulos funcionales del sistema  
✔ No omite ninguna tabla obligatoria según la versión del diccionario  
✔ Incluye tablas opcionales recomendadas por buenas prácticas  

---

## **7. Estado del Documento**

Este documento es la **versión oficial de organización del backend**, listo para ser presentado a profesores, revisores, jefes de proyecto o compañeros del equipo.

