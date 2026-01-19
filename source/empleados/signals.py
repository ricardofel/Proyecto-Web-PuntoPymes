from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Q
from usuarios.models import Usuario
from empleados.models import Empleado, Contrato
from notificaciones.services.notificacion_service import NotificacionService
from notificaciones.constants import TiposNotificacion
from auditoria.middleware import get_current_user 

# --- 1. LÓGICA DE SINCRONIZACIÓN ---
@receiver(post_save, sender=Empleado)
def sync_empleado_con_usuario(sender, instance, created, **kwargs):
    """Sincroniza cuenta de usuario al guardar un empleado."""
    email = (instance.email or "").strip().lower()
    if not email: return

    user, _ = Usuario.objects.get_or_create(
        email=email,
        defaults={"empleado": instance, "estado": True},
    )

    if user.empleado_id != instance.id:
        user.empleado = instance

    estado_empleado = (instance.estado or "").strip().lower()
    user.estado = (estado_empleado == "activo")
    user.save(update_fields=["empleado", "estado"])

# --- 2. LÓGICA DE NOTIFICACIONES ---

@receiver(post_save, sender=Empleado)
def notificaciones_creacion_empleado(sender, instance, created, **kwargs):
    """Gestiona las alertas cuando nace un nuevo registro de empleado."""
    if created:
        creador = get_current_user()
        
        if creador and creador.is_authenticated:
            NotificacionService.crear_notificacion(
                usuario=creador,
                titulo="Registro Exitoso",
                mensaje=f"Has registrado correctamente al empleado {instance.nombres} {instance.apellidos}.",
                tipo=TiposNotificacion.EXITO,
                url="/empleados/lista/"
            )

        admins_rrhh = Usuario.objects.filter(
            Q(is_superuser=True) | Q(is_staff=True)
        ).exclude(id=creador.id if creador else None)

        for admin in admins_rrhh:
            NotificacionService.crear_notificacion(
                usuario=admin,
                titulo="Nuevo Ingreso",
                mensaje=f"Se ha incorporado {instance.nombres} {instance.apellidos} al equipo.",
                tipo=TiposNotificacion.INFO,
                url=f"/empleados/editar/{instance.id}/"
            )

@receiver(post_save, sender=Contrato)
def notificar_nuevo_contrato(sender, instance, created, **kwargs):
    """Avisa al empleado cuando tiene un nuevo contrato."""
    if created and instance.empleado.usuario:
        NotificacionService.crear_notificacion(
            usuario=instance.empleado.usuario,
            titulo="Nuevo Documento Legal",
            mensaje=f"Se ha cargado un contrato '{instance.tipo}' en tu perfil.",
            tipo=TiposNotificacion.INFO,
            url=f"/empleados/lista-contratos/{instance.empleado.id}/"
        )

@receiver(pre_save, sender=Empleado)
def notificar_cambio_puesto(sender, instance, **kwargs):
    """Detecta y celebra los ascensos o cambios de puesto."""
    if instance.pk and instance.usuario:
        try:
            old = Empleado.objects.get(pk=instance.pk)
            if instance.puesto != old.puesto:
                nuevo = instance.puesto.nombre if instance.puesto else "Sin Asignar"
                NotificacionService.crear_notificacion(
                    usuario=instance.usuario,
                    titulo="Actualización Laboral",
                    mensaje=f"Tu cargo ha sido actualizado a: {nuevo}.",
                    tipo=TiposNotificacion.EXITO,
                    url="/usuarios/perfil/"
                )
        except Empleado.DoesNotExist:
            pass