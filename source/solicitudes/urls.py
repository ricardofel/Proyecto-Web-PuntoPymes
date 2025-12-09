from django.urls import path
from . import views

app_name = 'solicitudes'

urlpatterns = [
    # Ruta principal (Lista)
    path('', views.lista_solicitudes_view, name='lista_solicitudes'),
    
    # 📌 CORRECCIÓN IMPORTANTE AQUÍ:
    # Hemos agregado <int:solicitud_id> para que la URL acepte el ID (ej: responder/2/)
    path('responder/<int:solicitud_id>/', views.responer_solicitudes_view, name='responder_solicitudes'),
    
    # Vista de empleado
    path('emp/', views.empleado_view, name='vista_empleado'), 
    
    # Crear nueva solicitud
    path('nueva/', views.crear_solicitud_view, name='crear_solicitud'), 
]