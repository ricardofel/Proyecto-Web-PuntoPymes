# usuarios/views/usuarios_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from usuarios.models import Rol
from usuarios.decorators import solo_superusuario_o_admin_rrhh

# IMPORTANTE: Hemos agregado PerfilUsuarioForm a los imports
from ..forms import UsuarioForm, PerfilUsuarioForm

User = get_user_model()

@login_required
@solo_superusuario_o_admin_rrhh
def lista_usuarios(request):
    """
    Listado de usuarios refactorizado.
    """
    # 1. Recuperar parámetros
    q = request.GET.get("q", "")
    filtro_estado = request.GET.get("estado", "")
    filtro_rol = request.GET.get("rol", "")
    
    # 2. Iniciar QuerySet con permisos base (usando nuestro nuevo método)
    usuarios = User.objects.visibles_para(request.user)

    # 3. Aplicar filtro de empresa global (caso Superuser Multi-tenant)
    # Este viene del middleware o sesión, no del modelo directamente
    empresa_actual = getattr(request, 'empresa_actual', None)
    if request.user.is_superuser and empresa_actual:
        usuarios = usuarios.para_empresa(empresa_actual)

    # 4. Encadenar filtros (Fluent Interface)
    usuarios = (
        usuarios
        .busqueda_general(q)
        .filtrar_por_estado(filtro_estado)
        .filtrar_por_rol(filtro_rol)
        .distinct()
        .order_by('-fecha_creacion')
    )

    # Contexto
    roles = Rol.objects.filter(estado=True).order_by("nombre")
    
    context = {
        "usuarios": usuarios,
        "titulo": "Gestión de Usuarios",
        "q": q,
        "filtro_estado": filtro_estado,
        "filtro_rol": filtro_rol,
        "roles": roles,
        # 'empresa_actual' ya suele estar en el contexto por procesadores, pero por si acaso:
        "empresa_actual": empresa_actual 
    }
    return render(request, "usuarios/lista_usuarios.html", context)

@login_required
@solo_superusuario_o_admin_rrhh
def gestionar_usuario(request, user_id=None):
    """
    Crear o editar un usuario (Admin/RRHH).
    - Si viene user_id => editar.
    - Si no viene => crear.
    """
    if user_id:
        usuario = get_object_or_404(User, pk=user_id)
        titulo = "Editar Usuario"
    else:
        usuario = None
        titulo = "Crear Nuevo Usuario"

    # 🛡️ Si el usuario objetivo es superuser y quien edita NO lo es → bloqueo
    if usuario and usuario.is_superuser and not request.user.is_superuser:
        messages.error(
            request,
            "No tienes permisos para editar a un superadministrador del sistema.",
        )
        return redirect("usuarios:lista_usuarios")

    if request.method == "POST":
        form = UsuarioForm(
            request.POST,
            instance=usuario,
            usuario_actual=request.user,
        )
        if form.is_valid():
            form.save()
            mensaje = (
                "Usuario creado exitosamente."
                if usuario is None
                else "Usuario actualizado exitosamente."
            )
            messages.success(request, mensaje)
            return redirect("usuarios:lista_usuarios")
    else:
        form = UsuarioForm(instance=usuario, usuario_actual=request.user)

    context = {
        "form": form,
        "titulo": titulo,
    }
    return render(request, "usuarios/form_usuario.html", context)


# ==========================================
# NUEVA VISTA PARA "MI PERFIL"
# ==========================================

@login_required
def perfil_usuario(request):
    """
    Vista para que el usuario logueado gestione sus propios datos
    (foto y teléfono) sin permisos administrativos.
    """
    usuario = request.user
    
    if request.method == 'POST':
        # request.FILES es necesario para procesar la imagen subida
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=usuario)
        
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado correctamente!')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Por favor corrige los errores indicados en el formulario.')
    else:
        form = PerfilUsuarioForm(instance=usuario)

    context = {
        'form': form,
        'usuario': usuario,
        'titulo': 'Mi Perfil'
    }
    return render(request, 'usuarios/perfil.html', context)