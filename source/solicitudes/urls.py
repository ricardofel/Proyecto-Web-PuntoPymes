from django.urls import path
from . import views

app_name = 'solicitudes'

urlpatterns = [
    # Ruta principal (Lista)
    path('', views.lista_solicitudes_view, name='lista_solicitudes'),
    
    # Ruta de detalle que recibe el ID (ej: /responder/5/)
    path('responder/<int:solicitud_id>/', views.responer_solicitudes_view, name='responder_solicitudes'),
    
    # Vista de empleado
    path('emp/', views.empleado_view, name='vista_empleado'), 
    
    # Crear nueva solicitud
    path('nueva/', views.crear_solicitud_view, name='crear_solicitud'), 
]