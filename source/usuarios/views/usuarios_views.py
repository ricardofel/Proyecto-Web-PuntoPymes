# usuarios/views/usuarios_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from usuarios.models import Rol
from usuarios.decorators import solo_superusuario_o_admin_rrhh

from ..forms import UsuarioForm

User = get_user_model()


@login_required
@solo_superusuario_o_admin_rrhh
def lista_usuarios(request):
    """
    Listado de usuarios con búsqueda y filtros por estado y rol.
    """
    q = request.GET.get("q", "").strip()
    filtro_estado = request.GET.get("estado", "").strip()
    filtro_rol = request.GET.get("rol", "").strip()

    usuarios = (
        User.objects.select_related("empleado")
        .prefetch_related("roles_asignados")
        .all()
    )

    # Búsqueda por correo o nombre del empleado
    if q:
        usuarios = usuarios.filter(
            Q(email__icontains=q)
            | Q(empleado__nombres__icontains=q)
            | Q(empleado__apellidos__icontains=q)
        )

    # Filtro por estado (activo / inactivo)
    if filtro_estado == "activo":
        usuarios = usuarios.filter(estado=True)
    elif filtro_estado == "inactivo":
        usuarios = usuarios.filter(estado=False)

    # Filtro por rol
    if filtro_rol:
        usuarios = usuarios.filter(roles_asignados__nombre=filtro_rol)

    usuarios = usuarios.distinct()

    # Roles disponibles para el combo de filtros
    roles = Rol.objects.filter(estado=True).order_by("nombre")

    context = {
        "usuarios": usuarios,
        "titulo": "Gestión de Usuarios",
        "q": q,
        "filtro_estado": filtro_estado,
        "filtro_rol": filtro_rol,
        "roles": roles,
    }
    return render(request, "usuarios/lista_usuarios.html", context)


@login_required
@solo_superusuario_o_admin_rrhh
def gestionar_usuario(request, user_id=None):
    """
    Crear o editar un usuario.
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
            usuario_actual=request.user,  # 👈 importante
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
