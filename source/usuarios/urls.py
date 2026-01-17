from django.urls import path
from usuarios.views.usuarios_views import (
    listar_usuarios, 
    crear_usuario, 
    editar_usuario, 
    eliminar_usuario,
    cambiar_estado_usuario,
    perfil_usuario  # <--- IMPORTANTE: Importamos la vista nueva
)

app_name = "usuarios"

urlpatterns = [
    path("", listar_usuarios, name="lista_usuarios"),
    
    # URL RESTAURADA:
    path("perfil/", perfil_usuario, name="perfil"),

    path("crear/", crear_usuario, name="crear_usuario"),
    path("<int:pk>/editar/", editar_usuario, name="editar_usuario"),
    path("<int:pk>/eliminar/", eliminar_usuario, name="eliminar_usuario"),
    path("<int:pk>/estado/", cambiar_estado_usuario, name="cambiar_estado"),
]