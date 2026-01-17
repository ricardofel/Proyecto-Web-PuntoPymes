from django.urls import path
from . import views

app_name = 'solicitudes'

urlpatterns = [
    # === VISTAS GENERALES ===
    # Lista principal (Admin ve todas, Empleado redirige)
    path('', views.lista_solicitudes_view, name='lista_solicitudes'),
    
    # Vista exclusiva del empleado (Mis solicitudes)
    path('emp/', views.empleado_view, name='vista_empleado'), 
    
    # Gestionar solicitud (Jefe/RRHH aprueba o rechaza)
    path('responder/<int:solicitud_id>/', views.responer_solicitudes_view, name='responder_solicitudes'),
    
    # === CRUD SOLICITUDES ===
    path('nueva/', views.crear_solicitud_view, name='crear_solicitud'), 
    path('editar/<int:solicitud_id>/', views.editar_solicitud_view, name='editar_solicitud'),
    path('eliminar/<int:solicitud_id>/', views.eliminar_solicitud_view, name='eliminar_solicitud'),

    # === RUTAS PARA ADJUNTOS (Soporte de Múltiples Archivos) ===
    
    # 1. Descargar un archivo específico 
    # NOTA: Recibe 'adjunto_id' (el ID del archivo en la tabla AdjuntoSolicitud), NO de la solicitud.
    path('documento/<int:adjunto_id>/', views.descargar_adjunto_view, name='descargar_adjunto'),
    
    # 2. Eliminar archivo específico (AJAX)
    # Esta ruta es llamada por el JavaScript cuando das clic en la "X"
    path('eliminar-adjunto/<int:adjunto_id>/', views.eliminar_adjunto_ajax, name='eliminar_adjunto_ajax'),
]