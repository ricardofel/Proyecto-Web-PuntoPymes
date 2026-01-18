from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model

from usuarios.forms import UsuarioForm, UsuarioEdicionForm, PerfilUsuarioForm
from usuarios.decorators import solo_superusuario_o_admin_rrhh

User = get_user_model()

@login_required
@solo_superusuario_o_admin_rrhh
def listar_usuarios(request):
    """
    Lista usuarios del sistema aplicando reglas de visibilidad jerárquica:
    1. Superusuarios: Ven TODOS los usuarios (Global), sin importar la empresa seleccionada.
    2. Admin RRHH: Ven SOLO los usuarios que pertenecen a su empresa actual.
    """
    empresa_actual = getattr(request, 'empresa_actual', None)
    query = request.GET.get('q', '').strip()

    # 1. Consulta Base Optimizada (Traemos todo inicialmente)
    usuarios_list = User.objects.select_related(
        'empleado', 
        'empleado__empresa', 
        'empleado__puesto'
    ).prefetch_related('roles_asignados').order_by('-fecha_creacion')

    # 2. Aplicación de Reglas de Visibilidad
    if request.user.is_superuser:
        # REGLA 1: El Superusuario tiene visión global absoluta.
        pass
    
    elif empresa_actual:
        # REGLA 2: El Admin RRHH está restringido a su empresa.
        usuarios_list = usuarios_list.filter(empleado__empresa=empresa_actual)
    
    else:
        # REGLA 3: Seguridad por defecto.
        # Si no es superusuario y no tiene contexto de empresa, no ve nada.
        usuarios_list = usuarios_list.none()

    # 3. Búsqueda por texto (Email, Nombres, Apellidos, Cédula)
    if query:
        usuarios_list = usuarios_list.filter(
            Q(email__icontains=query) |
            Q(empleado__nombres__icontains=query) |
            Q(empleado__apellidos__icontains=query) |
            Q(empleado__cedula__icontains=query)
        )

    # 4. Paginación (10 items por página)
    paginator = Paginator(usuarios_list, 10)
    page_number = request.GET.get('page')
    usuarios = paginator.get_page(page_number)

    return render(request, 'usuarios/lista_usuarios.html', {
        'usuarios': usuarios,
        'q': query
    })

@login_required
@solo_superusuario_o_admin_rrhh
def crear_usuario(request):
    # Crea un usuario mediante el formulario (incluye usuario_actual para reglas de permisos)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, usuario_actual=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Usuario '{user.email}' creado exitosamente.")
            return redirect('usuarios:lista_usuarios')
    else:
        form = UsuarioForm(usuario_actual=request.user)

    return render(request, 'usuarios/form_usuario.html', {
        'form': form,
        'titulo': 'Crear Nuevo Usuario'
    })

@login_required
@solo_superusuario_o_admin_rrhh
def editar_usuario(request, pk):
    # Edita un usuario existente
    usuario = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UsuarioEdicionForm(request.POST, request.FILES, instance=usuario, usuario_actual=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usuario '{usuario.email}' actualizado.")
            return redirect('usuarios:lista_usuarios')
    else:
        form = UsuarioEdicionForm(instance=usuario, usuario_actual=request.user)

    return render(request, 'usuarios/form_usuario.html', {
        'form': form,
        'titulo': f'Editar Usuario: {usuario.email}'
    })

@login_required
@solo_superusuario_o_admin_rrhh
def eliminar_usuario(request, pk):
    # Elimina un usuario (con protección para no eliminarse a sí mismo)
    usuario = get_object_or_404(User, pk=pk)

    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propio usuario.")
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")
        return redirect('usuarios:lista_usuarios')

    return render(request, 'core/confirmar_eliminar.html', {
        'obj': usuario,
        'titulo': 'Eliminar Usuario',
        'mensaje': f'¿Estás seguro de eliminar al usuario {usuario.email}? Esta acción no se puede deshacer.'
    })

@login_required
@solo_superusuario_o_admin_rrhh
def cambiar_estado_usuario(request, pk):
    # Activa / desactiva el usuario alternando el campo personalizado "estado"
    usuario = get_object_or_404(User, pk=pk)

    if usuario == request.user:
        messages.error(request, "No puedes desactivar tu propio usuario.")
    else:
        usuario.estado = not usuario.estado
        usuario.save()

        estado_txt = "activado" if usuario.estado else "desactivado"
        messages.success(request, f"Usuario {usuario.email} {estado_txt}.")

    return redirect('usuarios:lista_usuarios')

@login_required
def perfil_usuario(request):
    """
    Permite al usuario autenticado editar sus datos básicos (foto y teléfono).
    """
    usuario = request.user

    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu perfil ha sido actualizado.")
            return redirect('usuarios:perfil')
    else:
        form = PerfilUsuarioForm(instance=usuario)

    return render(request, 'usuarios/perfil.html', {
        'form': form,
        'usuario': usuario
    })
