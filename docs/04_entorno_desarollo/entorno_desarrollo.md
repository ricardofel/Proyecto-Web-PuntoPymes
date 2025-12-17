# 🟦 TalentTrack – Entorno de Desarrollo (Backend)

Este documento describe los pasos necesarios para levantar el entorno backend de TalentTrack en cualquier máquina nueva. Siguiendo este documento paso a paso, el proyecto debe ejecutarse correctamente sin errores.

---

# 1️⃣ Requisitos previos

- Python 3.11
- PostgreSQL ≥ 14
- Git
- Visual Studio Code

---

# 2️⃣ Clonar el repositorio

```bash
git clone <URL_DEL_REPO>
cd <CARPETA_DEL_PROYECTO>
```

---

# 3️⃣ Crear y activar el entorno virtual

```bash
py -3.11 -m venv venv
```

Activar:

Windows:

```bash
venv\Scripts\activate
```

Deberías ver algo como:

```
(venv) PS C:\Proyecto-Web-PuntoPymes>
```

---

# 4️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

Incluye paquetes como:

- Django
- Django REST Framework
- psycopg2
- django-environ
- tailwind
- etc

---

# 5️⃣ Configurar la base de datos PostgreSQL

Abrir pgAdmin y conectarse como usuario:

```
postgres
```

Luego ejecutar:

```sql
CREATE DATABASE talenttrack_dev;
CREATE USER talent_user WITH PASSWORD 'talent_pass';
GRANT ALL PRIVILEGES ON DATABASE talenttrack_dev TO talent_user;
GRANT ALL ON SCHEMA public TO talent_user;
ALTER SCHEMA public OWNER TO talent_user;
```

---

# 6️⃣ Crear el archivo .env

Moverse a:

```
cd source
```

Copiar:

```bash
copy .env.example .env
```

Verificar contenido del `.env`:

```
DEBUG=True
SECRET_KEY=<<REPLACE_WITH_SECRET_KEY>>

ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=puntopymes_dev
DB_USER=postgres
DB_PASSWORD=<<REPLACE_WITH_PASSWORD>>
DB_HOST=localhost
DB_PORT=5432

TAILWIND_APP_NAME=theme
```

---

# 7️⃣ Aplicar migraciones

```bash
python manage.py migrate
```

---

# 8️⃣ Crear súperusuario

```bash
python manage.py createsuperuser
```

---

# 9️⃣ Ejecutar servidor

```bash
python manage.py runserver
```

Abrir:

```
http://127.0.0.1:8000/
http://127.0.0.1:8000/admin/
```

---

# 🔍 Comprobación manual

✔ Server funciona
✔ Admin carga
✔ Migraciones aplicadas
✔ Tablas creadas

---

# ❗ Solución a error común de permisos

```sql
GRANT ALL ON SCHEMA public TO talent_user;
ALTER SCHEMA public OWNER TO talent_user;
```

---

# 🧠 Estructura del proyecto

```
Proyecto-Web-PuntoPymes/
│
├── source/
│   ├── talenttrack/      # Configuración global (settings, urls, api_router)
│   ├── <apps del proyecto>  # core, empleados, usuarios, asistencia, etc.
│   ├── manage.py
│   ├── .env
│   └── .env.example
│
├── venv/
├── requirements.txt
├── ENTORNO_DESARROLLO.md
├── .gitignore
├── LICENSE
└── README.md

```

---

# 🙅‍♂️ Archivos que NO van a git

- venv/
- source/.env
- __pycache__/
- *.pyc
- media/
- staticfiles/

---

# 🟦 Checklist rápido

1. Clonar
2. Crear venv
3. Instalar requirements
4. Crear BD
5. Crear usuario
6. Dar permisos
7. Configurar .env
8. Migrar
9. Superusuario
10. Runserver

---

# 💙 Contacto técnico

Cualquier problema → contactar a Queen. Besos
