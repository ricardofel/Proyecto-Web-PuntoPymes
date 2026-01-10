from django.urls import path
from notificaciones.views.notificaciones_view import listar_notificaciones, marcar_todas_leidas

app_name = "notificaciones"

urlpatterns = [
    path('', listar_notificaciones, name='listar'),

    path('marcar-todas/', marcar_todas_leidas, name='marcar_todas'),
]