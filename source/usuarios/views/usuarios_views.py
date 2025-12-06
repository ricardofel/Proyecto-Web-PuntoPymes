# usuarios/views/usuarios_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from usuarios.decorators import solo_admin_usuarios

from ..forms import UsuarioForm

User = get_user_model()


@login_required
@solo_admin_usuarios
def lista_usuarios(request):
    """
    Vista de listado de usuarios.
    Por ahora solo carga todos los usuarios y los pasa a la plantilla.
    """
    usuarios = (
        User.objects.select_related("empleado")
        .prefetch_related("roles_asignados")
        .all()
    )

    context = {
        "usuarios": usuarios,
        "titulo": "Gestión de Usuarios",
    }
    return render(request, "usuarios/lista_usuarios.html", context)


@login_required
@solo_admin_usuarios
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

    if request.method == "POST":
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save()
            mensaje = (
                "Usuario creado exitosamente."
                if usuario is None
                else "Usuario actualizado exitosamente."
            )
            messages.success(request, mensaje)
            # Ojo: usa el namespace 'usuarios' si lo registraste así en urls.py
            return redirect("usuarios:lista_usuarios")
    else:
        form = UsuarioForm(instance=usuario)

    context = {
        "form": form,
        "titulo": titulo,
    }
    return render(request, "usuarios/form_usuario.html", context)
