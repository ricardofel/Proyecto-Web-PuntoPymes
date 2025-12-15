# source/usuarios/signals.py
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
    if not request: return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff: return xff.split(",")[0].strip()
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
    email = credentials.get("username")
    logger.warning("LOGIN FAIL email=%s ip=%s ua=%s", email, ip, ua)

@receiver(post_save, sender=Empleado)
def crear_usuario_para_empleado(sender, instance, created, **kwargs):
    """
    Crea usuario automáticamente. CORREGIDO para usar 'estado' en lugar de 'is_active'.
    """
    if not created:
        return

    # Si ya tiene usuario, no hacemos nada
    if hasattr(instance, "usuario") and instance.usuario is not None:
        return

    email_empleado = instance.email
    if not email_empleado:
        return

    email_normalizado = email_empleado.strip().lower()

    if User.objects.filter(email=email_normalizado).exists():
        return

    # --- AQUÍ ESTABA EL ERROR ---
    # Usamos 'estado=False' porque tu modelo Usuario NO tiene campo is_active escribible.
    user = User.objects.create_user(
        email=email_normalizado,
        password=None, 
        empleado=instance,
        estado=False,  # <--- CORRECCIÓN: Usamos tu campo personalizado 'estado'
    )

    rol_empleado = Rol.objects.filter(nombre="Empleado").first()
    if rol_empleado:
        UsuarioRol.objects.create(usuario=user, rol=rol_empleado)
        
        user.is_superuser = False
        user.is_staff = False
        user.save(update_fields=["is_superuser", "is_staff"])

@receiver(post_save, sender=User)
def sync_superuser_role(sender, instance, created, **kwargs):
    if not instance.is_superuser:
        return
    rol_super, _ = Rol.objects.get_or_create(
        nombre="Superusuario",
        defaults={"descripcion": "Super Admin", "estado": True},
    )
    if UsuarioRol.objects.filter(usuario=instance, rol=rol_super).exists():
        return
    UsuarioRol.objects.create(usuario=instance, rol=rol_super)