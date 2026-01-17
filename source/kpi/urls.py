from django.urls import path
from .views.kpi_view import (
    dashboard_view, 
    kpi_recalcular_global_view, # <--- ¡Agregado aquí!
    kpi_generar_default_view, 
    kpi_detalle_view, 
    kpi_recalcular_view,
    kpi_editar_view,
    kpi_eliminar_view
)

app_name = "kpi"

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    # Corregido: ya no dice "kpi_view.kpi_recalcular..."
    path("recalcular/", kpi_recalcular_global_view, name="recalcular_global"),
    path("generar-defaults/", kpi_generar_default_view, name="kpi_generar_defaults"),
    path("<int:pk>/", kpi_detalle_view, name="kpi_detalle"),
    path("<int:pk>/recalcular/", kpi_recalcular_view, name="kpi_recalcular"),
    path("<int:pk>/editar/", kpi_editar_view, name="kpi_editar"),
    path("<int:pk>/eliminar/", kpi_eliminar_view, name="kpi_eliminar"),
]