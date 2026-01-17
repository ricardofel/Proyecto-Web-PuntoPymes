from django.db import transaction
from django.contrib.auth import get_user_model
from usuarios.models import Rol, UsuarioRol
from empleados.models import Empleado
from usuarios.constants import NombresRoles  # ¡Importamos las constantes!

User = get_user_model()

class UsuarioService:
    @staticmethod
    @transaction.atomic
    def crear_o_actualizar_usuario(usuario, data, editor):
        """
        Maneja la lógica completa de guardar un usuario.
        
        :param usuario: Instancia de Usuario (puede ser nueva o existente).
        :param data: Diccionario con datos limpios (cleaned_data del form).
        :param editor: El usuario que está realizando la acción (request.user).
        :return: El usuario guardado.
        """
        
        # 1. Manejo de Contraseña
        nuevo_password = data.get('nuevo_password')
        if nuevo_password:
            usuario.set_password(nuevo_password)
        
        # 2. Protección de campos si el editor NO es superusuario
        if not editor.is_superuser:
            if usuario.pk:
                # Recuperamos el original de la BD para no perder permisos
                usuario_original = User.objects.get(pk=usuario.pk)
                usuario.is_staff = usuario_original.is_staff
                usuario.is_superuser = usuario_original.is_superuser
                # Si no se envió empleado, mantenemos el anterior
                if 'empleado' not in data: 
                    usuario.empleado = usuario_original.empleado
            else:
                usuario.is_staff = False
                usuario.is_superuser = False

        # Guardamos los datos básicos del usuario
        usuario.save()

        # 3. Gestión de Roles (Solo Superusuario)
        if editor.is_superuser:
            rol_seleccionado = data.get('roles')
            
            # Limpiamos roles anteriores
            UsuarioRol.objects.filter(usuario=usuario).delete()

            if rol_seleccionado:
                UsuarioRol.objects.create(usuario=usuario, rol=rol_seleccionado)
                
                # Lógica de permisos basada en constantes (Adiós Magic Strings)
                if rol_seleccionado.nombre == NombresRoles.SUPERUSUARIO:
                    usuario.is_superuser = True
                    usuario.is_staff = True
                elif rol_seleccionado.nombre == NombresRoles.ADMIN_RRHH:
                    usuario.is_superuser = False
                    usuario.is_staff = True
                else:
                    usuario.is_superuser = False
                    usuario.is_staff = False
                
                # Actualizamos flags de permisos sin disparar señales innecesarias
                usuario.save(update_fields=["is_superuser", "is_staff"])

        # 4. Sincronización con Empleado (Estado)
        if usuario.empleado:
            nuevo_estado_empleado = (
                Empleado.Estado.ACTIVO if usuario.estado else Empleado.Estado.INACTIVO
            )
            if usuario.empleado.estado != nuevo_estado_empleado:
                usuario.empleado.estado = nuevo_estado_empleado
                usuario.empleado.save(update_fields=["estado"])

        return usuario