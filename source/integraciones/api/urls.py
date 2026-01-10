from django.urls import path
from .views import exportar_nomina_api, importar_empleados_api, exportar_asistencia_api

urlpatterns = [
    path('nomina/exportar/', exportar_nomina_api, name='api_nomina_export'),
    path('empleados/importar/', importar_empleados_api, name='api_empleados_import'),
    path('asistencia/eventos/', exportar_asistencia_api, name='api_asistencia_export'),
]