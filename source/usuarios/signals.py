import logging
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from empleados.models import Empleado
from .models import Rol, UsuarioRol, Usuario
from .constants import NombresRoles 

from notificaciones.services.notificacion_service import NotificacionService
from notificaciones.constants import TiposNotificacion

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


@receiver(post_save, sender=Usuario)
def notificar_nuevo_usuario(sender, instance, created, **kwargs):
    """Bienvenida al sistema tras crear el usuario."""
    if created:
        NotificacionService.crear_notificacion(
            usuario=instance,
            titulo="¡Bienvenido a PuntoPymes!",
            mensaje="Tu cuenta ha sido creada exitosamente. Configura tu perfil para comenzar.",
            tipo=TiposNotificacion.EXITO,
            url="/usuarios/perfil/"
        )

@receiver(pre_save, sender=Usuario)
def notificar_cambio_password(sender, instance, **kwargs):
    """Alerta de seguridad si cambia la contraseña."""
    if instance.pk:
        try:
            old_user = Usuario.objects.get(pk=instance.pk)
            if instance.password != old_user.password:
                NotificacionService.crear_notificacion(
                    usuario=instance,
                    titulo="Seguridad: Cambio de Contraseña",
                    mensaje="Tu contraseña ha sido actualizada. Si no fuiste tú, contacta a soporte inmediatamente.",
                    tipo=TiposNotificacion.ALERTA,
                    url="/usuarios/perfil/"
                )
        except Usuario.DoesNotExist:
            pass

@receiver(post_save, sender=UsuarioRol)
def notificar_asignacion_rol(sender, instance, created, **kwargs):
    """Notifica cambios en los permisos (Roles)."""
    if created:
        NotificacionService.crear_notificacion(
            usuario=instance.usuario,
            titulo="Nuevos Permisos",
            mensaje=f"Se te ha asignado el rol de: {instance.rol.nombre}.",
            tipo=TiposNotificacion.INFO,
            url="/core/dashboard/"
        )