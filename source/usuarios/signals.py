import logging
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from empleados.models import Empleado
from .models import Rol, UsuarioRol
# IMPORTAMOS LAS CONSTANTES
from .constants import NombresRoles 

logger = logging.getLogger("auth")
User = get_user_model()

# ... (tus funciones _get_client_ip, log_user_login, etc. siguen igual) ...

@receiver(post_save, sender=Empleado)
def crear_usuario_para_empleado(sender, instance, created, **kwargs):
    if not created: return
    if hasattr(instance, "usuario") and instance.usuario is not None: return
    email_empleado = instance.email
    if not email_empleado: return

    email_normalizado = email_empleado.strip().lower()
    if User.objects.filter(email=email_normalizado).exists(): return

    user = User.objects.create_user(
        email=email_normalizado,
        password=None, 
        empleado=instance,
        estado=False,
    )

    # CORRECCIÓN: Usar constante
    rol_empleado = Rol.objects.filter(nombre=NombresRoles.EMPLEADO).first()
    if rol_empleado:
        UsuarioRol.objects.create(usuario=user, rol=rol_empleado)
        user.is_superuser = False
        user.is_staff = False
        user.save(update_fields=["is_superuser", "is_staff"])

@receiver(post_save, sender=User)
def sync_superuser_role(sender, instance, created, **kwargs):
    if not instance.is_superuser:
        return
    
    # CORRECCIÓN: Usar constante
    rol_super, _ = Rol.objects.get_or_create(
        nombre=NombresRoles.SUPERUSUARIO,
        defaults={"descripcion": "Super Admin", "estado": True},
    )
    if not UsuarioRol.objects.filter(usuario=instance, rol=rol_super).exists():
        UsuarioRol.objects.create(usuario=instance, rol=rol_super)