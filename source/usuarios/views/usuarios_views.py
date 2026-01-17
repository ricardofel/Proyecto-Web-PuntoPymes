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
    Lista todos los usuarios del sistema.
    """
    query = request.GET.get('q', '').strip()
    
    # CORRECCIÓN 1: Ordenamos por 'fecha_creacion', no 'date_joined'
    usuarios_list = User.objects.all().prefetch_related('groups').order_by('-fecha_creacion')

    if query:
        # CORRECCIÓN 2: Buscamos por email o datos del EMPLEADO (ya que el usuario no tiene nombres propios)
        usuarios_list = usuarios_list.filter(
            Q(email__icontains=query) |
            Q(empleado__nombres__icontains=query) |
            Q(empleado__apellidos__icontains=query)
        )

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
    usuario = get_object_or_404(User, pk=pk)
    
    if usuario == request.user:
        messages.error(request, "No puedes desactivar tu propio usuario.")
    else:
        # CORRECCIÓN 3: Solo alternamos 'estado' (tu campo personalizado)
        usuario.estado = not usuario.estado
        usuario.save()
        
        estado_txt = "activado" if usuario.estado else "desactivado"
        messages.success(request, f"Usuario {usuario.email} {estado_txt}.")
        
    return redirect('usuarios:lista_usuarios')

@login_required
def perfil_usuario(request):
    """
    Permite al usuario logueado editar sus propios datos básicos (foto, teléfono).
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