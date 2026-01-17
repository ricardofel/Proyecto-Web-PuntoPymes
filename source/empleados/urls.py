from django.urls import path 
from . import views 

app_name = "empleados"

urlpatterns = [
    # directorio principal (vista basada en clase)
    path('', views.ListaEmpleadosView.as_view(), name='lista_empleados'),

    # operaciones crud de empleados
    path('nuevo/', views.crear_empleado_view, name='crear_empleado'),
    path('editar/<int:pk>/', views.editar_empleado_view, name='editar_empleado'),
    
    # gestión de vinculaciones laborales (contratos)
    path('perfil/<int:empleado_id>/contratos/', views.lista_contratos_view, name='lista_contratos'),
    path('perfil/<int:empleado_id>/contratos/nuevo/', views.crear_contrato_view, name='crear_contrato'),

    # servicio de archivos protegidos (acceso a documentos privados)
    path('documentos-seguros/<path:filepath>/', views.servir_contrato_privado, name='ver_contrato_privado'),
    
    # endpoints utilitarios
    path('cambiar_estado/<int:pk>/', views.cambiar_estado_empleado_view, name='cambiar_estado_empleado'),
    path('editar/<int:pk>/foto/', views.actualizar_foto_view, name='actualizar_foto'),
]