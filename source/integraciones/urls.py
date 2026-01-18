from .views.dashboard_view import (
    integraciones_dashboard_view,
    logs_actualizados_view,
    probar_conexion_erp_view,
    cambiar_estado_erp_view,
    probar_webhook_view,
)

app_name = "integraciones"

urlpatterns = [
    path("", integraciones_dashboard_view, name="dashboard"),
    path("htmx/logs/", logs_actualizados_view, name="htmx_logs"),
    path("erp/<int:pk>/probar/", probar_conexion_erp_view, name="erp_probar"),
    path(
        "erp/<int:pk>/cambiar-estado/",
        cambiar_estado_erp_view,
        name="erp_cambiar_estado",
    ),
    path(
        "webhook/<int:pk>/probar/",
        probar_webhook_view,
        name="webhook_probar",
    ),
]
