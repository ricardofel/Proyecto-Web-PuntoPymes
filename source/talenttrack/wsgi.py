"""
Configuración WSGI para el proyecto TalentTrack.

Este módulo expone el callable WSGI a nivel de módulo con el nombre
``application``, utilizado por servidores de producción (Gunicorn, uWSGI, etc.).

Documentación oficial:
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Definición del módulo de configuración principal de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "talenttrack.settings")

# Callable WSGI utilizado por el servidor de aplicaciones
application = get_wsgi_application()
