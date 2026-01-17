from django.db import transaction
from django.contrib.auth import get_user_model
from usuarios.models import UsuarioRol
from empleados.models import Empleado
from usuarios.constants import NombresRoles

User = get_user_model()

class UsuarioService:
    @staticmethod
    @transaction.atomic
    def crear_o_actualizar_usuario(usuario, data, editor):
        """
        Crea o actualiza un usuario y sincroniza:
        - contraseña (si se envía),
        - roles (solo si el editor es superuser),
        - flags is_staff/is_superuser según el rol,
        - y estado del empleado asociado.
        """

        # Contraseña: solo se cambia si el campo viene con valor
        nuevo_password = data.get('nuevo_password')
        if nuevo_password:
            usuario.set_password(nuevo_password)

        # Restricciones para editores no superuser:
        # evita que modifiquen flags de permisos y, en edición, conserva valores originales.
        if not editor.is_superuser:
            if usuario.pk:
                usuario_original = User.objects.get(pk=usuario.pk)
                usuario.is_staff = usuario_original.is_staff
                usuario.is_superuser = usuario_original.is_superuser

                # Si el empleado no viene en data, se conserva el actual
                if 'empleado' not in data:
                    usuario.empleado = usuario_original.empleado
            else:
                # En creación por no superuser, fuerza permisos mínimos
                usuario.is_staff = False
                usuario.is_superuser = False

        # Persistencia de datos base del usuario
        usuario.save()

        # Gestión de roles: solo superuser puede modificar roles y permisos
        if editor.is_superuser:
            rol_seleccionado = data.get('roles')

            # Reinicia asignaciones previas para mantener un único rol efectivo
            UsuarioRol.objects.filter(usuario=usuario).delete()

            if rol_seleccionado:
                UsuarioRol.objects.create(usuario=usuario, rol=rol_seleccionado)

                # Asignación de flags según nombre del rol (uso de constantes)
                if rol_seleccionado.nombre == NombresRoles.SUPERUSUARIO:
                    usuario.is_superuser = True
                    usuario.is_staff = True
                elif rol_seleccionado.nombre == NombresRoles.ADMIN_RRHH:
                    usuario.is_superuser = False
                    usuario.is_staff = True
                else:
                    usuario.is_superuser = False
                    usuario.is_staff = False

                # Guarda solo campos de permisos
                usuario.save(update_fields=["is_superuser", "is_staff"])

        # Sincroniza el estado del empleado con el estado del usuario
        if usuario.empleado:
            nuevo_estado_empleado = (
                Empleado.Estado.ACTIVO if usuario.estado else Empleado.Estado.INACTIVO
            )
            if usuario.empleado.estado != nuevo_estado_empleado:
                usuario.empleado.estado = nuevo_estado_empleado
                usuario.empleado.save(update_fields=["estado"])

        return usuario
