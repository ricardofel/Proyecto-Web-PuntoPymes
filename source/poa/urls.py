from django.urls import path
from .views.poa_view import (
    poa_view,
    poa_dashboard_partial,
    objetivo_crear_view,
    objetivo_detalle_view,
)

app_name = "poa"

urlpatterns = [
    path("", poa_view, name="poa"),  # página completa
    path("dashboard/", poa_dashboard_partial, name="dashboard"),  # partial HTMX
    path("objetivos/crear/", objetivo_crear_view, name="objetivo_crear"),  # POST HTMX
    path("objetivos/<int:pk>/", objetivo_detalle_view, name="objetivo_detalle"),
]
