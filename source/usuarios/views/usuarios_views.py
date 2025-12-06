# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from usuarios.models import Usuario
from usuarios.forms import UsuarioForm


def gestionar_usuario(request, user_id=None):

    if user_id:
        usuario = get_object_or_404(Usuario, pk=user_id)
        titulo = "Editar Usuario"
    else:
        usuario = None
        titulo = "Crear Nuevo Usuario"

    if request.method == "POST":
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usuario {titulo.lower()} exitosamente.")
            return redirect("lista_usuarios")  # Asumiendo que tienes una lista
    else:
        form = UsuarioForm(instance=usuario)

    return render(
        request, "usuarios/form_usuario.html", {"form": form, "titulo": titulo}
    )


def lista_usuarios(request):
    # Obtenemos todos los usuarios
    # .select_related('empleado') -> Trae los datos del empleado en la misma consulta (optimización)
    # .prefetch_related('roles_asignados') -> Trae los roles eficientemente
    usuarios = (
        Usuario.objects.select_related("empleado")
        .prefetch_related("roles_asignados")
        .all()
    )

    context = {"usuarios": usuarios, "titulo": "Gestión de Usuarios"}

    return render(request, "usuarios/form_usuario.html", context)
