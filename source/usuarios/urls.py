# usuarios/urls.py
from django.urls import path
from .views.usuarios_views import gestionar_usuario, lista_usuarios

# --- AGREGA ESTA LÍNEA ---
app_name = "usuarios"
# -------------------------

urlpatterns = [
    path("lista/", lista_usuarios, name="lista_usuarios"),
    path("crear/", gestionar_usuario, name="crear_usuario"),
    path("editar/<int:user_id>/", gestionar_usuario, name="editar_usuario"),
]
