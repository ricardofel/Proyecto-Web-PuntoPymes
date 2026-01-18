from django.urls import path
from notificaciones.views.notificaciones_view import (
    lista_notificaciones,
    marcar_una_leida,
    marcar_todas_leidas,
    ver_detalle_notificacion
)

app_name = "notificaciones"

urlpatterns = [
    path("", lista_notificaciones, name="lista_notificaciones"),
    path("listar/", lista_notificaciones, name="listar"),
    path("marcar-todas/", marcar_todas_leidas, name="marcar_todas"),
    path("<int:pk>/leida/", marcar_una_leida, name="marcar_leida"),
    path("<int:pk>/detalle/", ver_detalle_notificacion, name="detalle"),
]