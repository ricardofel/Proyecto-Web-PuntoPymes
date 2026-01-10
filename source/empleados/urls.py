from django.urls import path
from . import views 

app_name = "empleados"

urlpatterns = [
    # --- 1. VISTA BASADA EN CLASE (La que acabamos de refactorizar) ---
    # Nota el .as_view() al final. Es obligatorio para las clases.
    path('', views.ListaEmpleadosView.as_view(), name='lista_empleados'),

    # codigo para mostrar todos los empleados de la DB sin filtros
    # path('lista/', views.ListaEmpleadosView.as_view(), name='lista_empleados'),

    # --- 2. VISTAS BASADAS EN FUNCIONES (Las antiguas) ---
    # Asumo que estas funciones siguen existiendo en tu views.py
    path('nuevo/', views.crear_empleado_view, name='crear_empleado'),
    path('editar/<int:pk>/', views.editar_empleado_view, name='editar_empleado'),
    
    # Gestión de Contratos y Estado
    path('perfil/<int:empleado_id>/contratos/', views.lista_contratos_view, name='lista_contratos'),
    path('cambiar_estado/<int:pk>/', views.cambiar_estado_empleado_view, name='cambiar_estado_empleado'),
    
    # Foto
    path('editar/<int:pk>/foto/', views.actualizar_foto_view, name='actualizar_foto'),
]
