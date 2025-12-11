# empleados/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from usuarios.models import Usuario  # usamos tu modelo custom


@receiver(post_save, sender="empleados.Empleado")
def sync_empleado_con_usuario(sender, instance, created, **kwargs):
    """
    Cada vez que se guarda un Empleado:

    - Busca o crea un Usuario con el mismo email
    - Vincula usuario.empleado = instance
    - Sincroniza usuario.estado según el estado del empleado
      (solo 'Activo' => True; el resto => False)
    """
    email = (instance.email or "").strip().lower()
    if not email:
        # Si el empleado no tiene correo, no hacemos nada
        return

    # 1) Buscar o crear usuario por email
    user, user_created = Usuario.objects.get_or_create(
        email=email,
        defaults={
            "empleado": instance,
            "estado": True,  # valor provisional, lo corregimos abajo
        },
    )

    # 2) Asegurar que el usuario quede vinculado al empleado
    if user.empleado_id != instance.id:
        user.empleado = instance

    # 3) Mapear estado del empleado -> estado del usuario
    #    (asumiendo que instance.estado es un CharField con esos textos)
    estado_empleado = (instance.estado or "").strip().lower()

    if estado_empleado == "activo":
        user.estado = True
    else:
        # Inactivo / Licencia / Suspendido => usuario NO puede entrar
        user.estado = False

    # Guardamos solo los campos que tocamos
    user.save(update_fields=["empleado", "estado"])
