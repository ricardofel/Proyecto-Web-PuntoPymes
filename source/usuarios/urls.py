from django.urls import path
from usuarios.views.usuarios_views import (
    listar_usuarios,
    crear_usuario,
    editar_usuario,
    eliminar_usuario,
    cambiar_estado_usuario,
    perfil_usuario,
)

app_name = "usuarios"

urlpatterns = [
    # Listado principal de usuarios
    path("", listar_usuarios, name="lista_usuarios"),

    # Perfil del usuario autenticado
    path("perfil/", perfil_usuario, name="perfil"),

    # Operaciones CRUD sobre usuarios
    path("crear/", crear_usuario, name="crear_usuario"),
    path("<int:pk>/editar/", editar_usuario, name="editar_usuario"),
    path("<int:pk>/eliminar/", eliminar_usuario, name="eliminar_usuario"),

    # Cambio de estado (activo / inactivo)
    path("<int:pk>/estado/", cambiar_estado_usuario, name="cambiar_estado"),
]
