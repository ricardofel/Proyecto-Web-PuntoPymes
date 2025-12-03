from django.urls import path
from core.views.home_views import home

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    # TODO: rutas de vistas web de core (Empresa, Unidades, Puestos, Turnos).
]
