# usuarios/urls.py
from django.urls import path
from .views.usuarios_views import lista_usuarios, gestionar_usuario

app_name = "usuarios"

urlpatterns = [
    path("", lista_usuarios, name="lista_usuarios"),
    path("nuevo/", gestionar_usuario, name="crear_usuario"),
    path("<int:user_id>/editar/", gestionar_usuario, name="editar_usuario"),
]
