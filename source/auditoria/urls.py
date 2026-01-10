from django.urls import path
# CORRECCIÓN: Importamos la FUNCIÓN específica desde el archivo
from auditoria.views.auditoria_view import auditoria_dashboard_view

app_name = "auditoria"

urlpatterns = [
    path('', auditoria_dashboard_view, name='dashboard'),
]