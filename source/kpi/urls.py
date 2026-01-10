from django.urls import path
from .views.kpi_view import (dashboard_view, 
                            kpi_crear_view, 
                            kpi_generar_default_view, 
                            kpi_detalle_view, 
                            kpi_recalcular_view)

app_name = "kpi"

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("crear/", kpi_crear_view, name="kpi_crear"),
    path("generar-defaults/", kpi_generar_default_view, name="kpi_generar_defaults"),
    path("<int:pk>/", kpi_detalle_view, name="kpi_detalle"),
    path("<int:pk>/recalcular/", kpi_recalcular_view, name="kpi_recalcular"),
]