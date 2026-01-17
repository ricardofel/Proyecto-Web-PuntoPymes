import logging
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from empleados.models import Empleado
from .models import Rol, UsuarioRol
from .constants import NombresRoles 

logger = logging.getLogger("auth")
User = get_user_model()


@receiver(post_save, sender=Empleado)
def crear_usuario_para_empleado(sender, instance, created, **kwargs):
    # Crea automáticamente un usuario para un empleado recién creado (si aplica)
    if not created: return
    if hasattr(instance, "usuario") and instance.usuario is not None: return

    email_empleado = instance.email
    if not email_empleado: return

    # Normaliza email y evita duplicados
    email_normalizado = email_empleado.strip().lower()
    if User.objects.filter(email=email_normalizado).exists(): return

    # Crea el usuario ligado al empleado; estado=False evita login inmediato
    user = User.objects.create_user(
        email=email_normalizado,
        password=None, 
        empleado=instance,
        estado=False,
    )

    # Asigna rol por defecto usando la enumeración/constantes del sistema
    rol_empleado = Rol.objects.filter(nombre=NombresRoles.EMPLEADO).first()
    if rol_empleado:
        UsuarioRol.objects.create(usuario=user, rol=rol_empleado)

        # Asegura que el usuario creado no sea staff/superuser
        user.is_superuser = False
        user.is_staff = False
        user.save(update_fields=["is_superuser", "is_staff"])


@receiver(post_save, sender=User)
def sync_superuser_role(sender, instance, created, **kwargs):
    # Sincroniza el rol de negocio cuando un usuario es superuser del sistema
    if not instance.is_superuser:
        return
    
    # Garantiza la existencia del rol "Superusuario" y lo asigna si falta
    rol_super, _ = Rol.objects.get_or_create(
        nombre=NombresRoles.SUPERUSUARIO,
        defaults={"descripcion": "Super Admin", "estado": True},
    )
    if not UsuarioRol.objects.filter(usuario=instance, rol=rol_super).exists():
        UsuarioRol.objects.create(usuario=instance, rol=rol_super)
