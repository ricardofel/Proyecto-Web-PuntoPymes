# Propuesta Técnica: Sistema de Gestión de Personal - PUNTO PYMES

> Integrantes: Ricardo Espinosa y Juan Diego Guerrero

## Resumen del Proyecto

El objetivo de este proyecto es la construcción de una **aplicación web integral** para la gestión de Talento Humano. El sistema a desarrollar será una solución moderna e intuitiva que centralizará la **información del personal**, el **seguimiento de sus actividades**, la **administración de ausencias** y el **control de asistencia** mediante geolocalización.

---

### Arquitectura del Sistema - (Sujeto a cambios)

La arquitectura se basará en un modelo cliente-servidor desacoplado, compuesto por dos componentes principales:

1.  **Frontend (Cliente Web):** Será la única interfaz de usuario del sistema, desarrollada como una Aplicación de Página Única (SPA). No se contempla el desarrollo de una aplicación móvil nativa; en su lugar, se asegurará un diseño completamente responsivo que garantice su correcta operación en navegadores de dispositivos móviles.
2.  **Backend (Servidor):** Constituirá el núcleo lógico y de persistencia de datos. Su función será procesar todas las peticiones, aplicar la lógica de negocio y comunicarse de forma segura con la base de datos a través de una API.

---

### Stack Tecnológico (Sujeto a cambios)

Para la construcción del sistema, se utilizarán las siguientes tecnologías:

* **Frontend:** Se desarrollará en **Angular**. La implementación se realizará como una **PWA (Progressive Web App)** para ofrecer una experiencia de usuario superior, permitiendo su "instalación" en la pantalla de inicio del dispositivo y optimizando su rendimiento general.

* **Backend:** El backend se implementará en **Node.js**, utilizando el framework **NestJS** para garantizar una arquitectura estructurada, mantenible y escalable. Se expondrá una **API RESTful** que servirá como punto único de comunicación para el frontend, gestionando las peticiones y devolviendo los datos en formato JSON.

* **Base de Datos:** El sistema de gestión de base de datos seleccionado es **PostgreSQL**. Se diseñará un esquema relacional sólido que garantice la integridad, consistencia y atomicidad de los datos.

* **Control de Versiones:** Se empleará **Git**, gestionando el código fuente en un repositorio centralizado (GitHub/GitLab) para un control de versiones efectivo.

* **Despliegue:** Se considera el uso de **Docker** para la contenerización de cada servicio (frontend, backend, base de datos). Esto estandarizará los entornos de desarrollo, pruebas y producción, simplificando el despliegue.

---

### Módulos Funcionales a Desarrollar

El proyecto se segmentará en los siguientes módulos funcionales:

1.  **Módulo de Administración de Personal:**
    * **Función:** Implementará las operaciones CRUD (Crear, Leer, Actualizar, Eliminar) para la gestión completa de los perfiles de empleados. Almacenará información personal, contractual y organizacional.
    * **Técnica:** Construcción de endpoints de API y vistas de interfaz para la administración directa de los registros en la base de datos.

2.  **Módulo de Plan Operativo Anual (POA) y Tareas:**
    * **Función:** Desarrollará la funcionalidad para registrar los objetivos anuales y desglosarlos en tareas asignables a cada empleado, permitiendo el seguimiento de su estado de avance.
    * **Técnica:** Para manejar datos con estructura variable (como checklists o comentarios), se utilizará el tipo de dato **JSONB** de PostgreSQL, evitando la sobre-normalización y aportando flexibilidad.

3.  **Módulo de Gestión de Ausencias:**
    * **Función:** Construirá un sistema para que los empleados soliciten permisos y vacaciones. Se implementará un flujo de aprobación para que los supervisores puedan gestionar dichas solicitudes a través de la plataforma.
    * **Técnica:** Diseño de un esquema de base de datos que incluya tablas como `solicitudes` con un campo de `estado` para gestionar el ciclo de vida de cada petición.

4.  **Módulo de Registro de Asistencia por GPS:**
    * **Función:** Implementará el registro de entrada/salida a través del navegador en dispositivos móviles.
    * **Técnica:** Se utilizará la **Geolocation API** nativa de los navegadores para obtener las coordenadas del usuario. Estas se enviarán a la API, donde el backend validará si se encuentran dentro de una **geocerca** (un área geográfica válida) predefinida. El registro se almacenará con su marca de tiempo y estado de validez.