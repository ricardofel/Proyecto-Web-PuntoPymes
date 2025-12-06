from django.urls import path
from . import views  # Importamos las vistas que creaste antes

app_name = "empleados"  # Mantenemos esto

urlpatterns = [
    path('lista/', views.lista_empleados_view, name='lista_empleados'),
    path('nuevo/', views.crear_empleado_view, name='crear_empleado'),
    path('editar/<int:pk>/', views.editar_empleado_view, name='editar_empleado'),
    path('perfil/<int:empleado_id>/contratos/', views.lista_contratos_view, name='lista_contratos'),
    path('cambiar_estado/<int:pk>/', views.cambiar_estado_empleado_view, name='cambiar_estado_empleado'),
    path('editar/<int:pk>/foto/', views.actualizar_foto_view, name='actualizar_foto'),
]
