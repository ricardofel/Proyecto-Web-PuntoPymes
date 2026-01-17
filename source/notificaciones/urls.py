from django.urls import path
from notificaciones.views.notificaciones_view import lista_notificaciones

app_name = "notificaciones"

urlpatterns = [
    # Usamos 'lista_notificaciones' (la función nueva)
    # Pero mantenemos el name='listar' para que no fallen tus templates antiguos
    path("", lista_notificaciones, name="listar"),
]