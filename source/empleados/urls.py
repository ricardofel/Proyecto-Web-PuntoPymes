from django.urls import path
from . import views  # Importamos las vistas que creaste antes

app_name = "empleados"  # Mantenemos esto

urlpatterns = [
    path('lista/', views.lista_empleados_view, name='lista_empleados'),
    path('nuevo/', views.crear_empleado_view, name='crear_empleado'),
]