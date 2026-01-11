from django.urls import path
# Importamos las vistas existentes y añadimos la nueva de perfil
# Asegúrate de que perfil_usuario esté en este archivo o ajusta la importación
from .views.usuarios_views import lista_usuarios, gestionar_usuario, perfil_usuario

app_name = "usuarios"

urlpatterns = [
    path("", lista_usuarios, name="lista_usuarios"),
    path("nuevo/", gestionar_usuario, name="crear_usuario"),
    path("<int:user_id>/editar/", gestionar_usuario, name="editar_usuario"),
    
    # Nueva ruta para el perfil
    path("perfil/", perfil_usuario, name="perfil"),
]