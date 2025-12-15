from django.urls import path
from . import views

app_name = 'solicitudes'

urlpatterns = [
    # Ruta principal (Lista - Admin/RRHH)
    path('', views.lista_solicitudes_view, name='lista_solicitudes'),
    
    # Ruta de detalle que recibe el ID (ej: /responder/5/)
    path('responder/<int:solicitud_id>/', views.responer_solicitudes_view, name='responder_solicitudes'),
    
    # Vista de empleado (Mis Solicitudes)
    path('emp/', views.empleado_view, name='vista_empleado'), 
    
    # Crear nueva solicitud
    path('nueva/', views.crear_solicitud_view, name='crear_solicitud'), 

    # --- ESTAS SON LAS RUTAS QUE FALTAN Y CAUSAN EL ERROR ---
    path('editar/<int:solicitud_id>/', views.editar_solicitud_view, name='editar_solicitud'),
    path('eliminar/<int:solicitud_id>/', views.eliminar_solicitud_view, name='eliminar_solicitud'),
]