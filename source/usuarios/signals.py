# usuarios/signals.py
import logging

from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save
from django.db import models
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from empleados.models import Empleado
from .models import Rol, UsuarioRol

logger = logging.getLogger("auth")
User = get_user_model()


def _get_client_ip(request):
    if not request:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = _get_client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "") if request else ""
    logger.info("LOGIN OK user=%s ip=%s ua=%s", user.email, ip, ua)


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    ip = _get_client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "") if request else ""
    email = credentials.get("username")  # aquí llega el email
    logger.warning("LOGIN FAIL email=%s ip=%s ua=%s", email, ip, ua)


@receiver(post_save, sender=Empleado)
def crear_usuario_para_empleado(sender, instance, created, **kwargs):
    """
    Cuando se crea un Empleado, se crea (si aplica) un Usuario vinculado 1–1.
    - Usa el correo del empleado.
    - Crea el usuario con password inutilizable.
    - Lo deja con estado=False (no puede loguearse aún).
    - Le asigna el rol 'Empleado' si existe.
    """

    # Solo cuando se crea (no en cada update)
    if not created:
        return

    # Si ya tiene usuario vinculado, no hacemos nada
    if hasattr(instance, "usuario") and instance.usuario is not None:
        return

    # ⚠️ AJUSTA ESTE NOMBRE AL CAMPO REAL DEL MODELO Empleado
    # ejemplo: instance.email, instance.correo, instance.correo_electronico, etc.
    email_empleado = instance.email

    if not email_empleado:
        # Sin correo, no creamos usuario
        return

    email_normalizado = email_empleado.strip().lower()

    # Evitar duplicar usuario si ya existe ese correo
    if User.objects.filter(email=email_normalizado).exists():
        return

    # Crear usuario vinculado al empleado
    user = User.objects.create_user(
        email=email_normalizado,
        password=None,  # password inutilizable, no puede entrar aún
        empleado=instance,
        estado=False,  # acceso desactivado hasta que RRHH lo active
    )

    # Asignar rol por defecto: 'Empleado'
    rol_empleado = Rol.objects.filter(nombre="Empleado", estado=True).first()
    if rol_empleado:
        UsuarioRol.objects.create(usuario=user, rol=rol_empleado)

        # Mapear a flags de Django
        user.is_superuser = False
        user.is_staff = False
        user.save(update_fields=["is_superuser", "is_staff"])
