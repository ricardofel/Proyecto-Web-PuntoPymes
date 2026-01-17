from django.urls import path 
from . import views 

app_name = "empleados"

urlpatterns = [
    # --- 1. VISTA BASADA EN CLASE ---
    path('', views.ListaEmpleadosView.as_view(), name='lista_empleados'),

    # --- 2. VISTAS BASADAS EN FUNCIONES ---
    path('nuevo/', views.crear_empleado_view, name='crear_empleado'),
    path('editar/<int:pk>/', views.editar_empleado_view, name='editar_empleado'),
    
    # --- Gestión de Contratos ---
    # Lista de contratos
    path('perfil/<int:empleado_id>/contratos/', views.lista_contratos_view, name='lista_contratos'),
    
    # Crear contrato (ESTA ES LA QUE FALTABA Y DABA ERROR)
    path('perfil/<int:empleado_id>/contratos/nuevo/', views.crear_contrato_view, name='crear_contrato'),

    # Ver PDF seguro (Necesaria para que el template lista_contratos no falle)
    path('documentos-seguros/<path:filepath>/', views.servir_contrato_privado, name='ver_contrato_privado'),
    
    # --- Acciones Extra ---
    path('cambiar_estado/<int:pk>/', views.cambiar_estado_empleado_view, name='cambiar_estado_empleado'),
    path('editar/<int:pk>/foto/', views.actualizar_foto_view, name='actualizar_foto'),
]