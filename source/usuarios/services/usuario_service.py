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
        Crea o actualiza un usuario.
        GARANTIZA que no se pierda el empleado asignado si el formulario envía None.
        """

        # Contraseña: solo se cambia si el campo viene con valor
        nuevo_password = data.get('nuevo_password')
        if nuevo_password:
            usuario.set_password(nuevo_password)

        if usuario.pk:
            # Obtenemos la versión actual de la base de datos
            usuario_original = User.objects.get(pk=usuario.pk)

            nuevo_empleado = data.get('empleado')
            
            if nuevo_empleado is None:
                usuario.empleado = usuario_original.empleado
        
        # Restricciones de permisos (Solo para NO superusuarios)
        if not editor.is_superuser:
            if usuario.pk:
                usuario.is_staff = usuario_original.is_staff
                usuario.is_superuser = usuario_original.is_superuser
            else:
                usuario.is_staff = False
                usuario.is_superuser = False

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
