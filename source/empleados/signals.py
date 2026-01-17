from django.db.models.signals import post_save
from django.dispatch import receiver
from usuarios.models import Usuario

@receiver(post_save, sender="empleados.Empleado")
def sync_empleado_con_usuario(sender, instance, created, **kwargs):
    """
    sincroniza automáticamente la cuenta de usuario cuando se modifica un empleado.
    - vincula el registro de usuario por email.
    - actualiza el acceso al sistema (user.estado) según el estado laboral.
    """
    email = (instance.email or "").strip().lower()
    
    # validación: sin email no es posible vincular usuario
    if not email:
        return

    # 1. gestión de cuenta de usuario asociada (buscar o crear)
    user, user_created = Usuario.objects.get_or_create(
        email=email,
        defaults={
            "empleado": instance,
            "estado": True, # valor inicial por defecto, se valida en el paso 3
        },
    )

    # 2. vinculación forzada de la relación fk
    if user.empleado_id != instance.id:
        user.empleado = instance

    # 3. sincronización de permisos de acceso
    # lógica de negocio: solo el estado 'activo' permite el inicio de sesión
    estado_empleado = (instance.estado or "").strip().lower()

    if estado_empleado == "activo":
        user.estado = True
    else:
        # estados como 'inactivo', 'licencia' o 'suspendido' revocan el acceso
        user.estado = False

    # persistencia optimizada de cambios
    user.save(update_fields=["empleado", "estado"])