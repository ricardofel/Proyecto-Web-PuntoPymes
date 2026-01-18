from django.urls import path
from . import views

app_name = 'solicitudes'

urlpatterns = [
    path('', views.lista_solicitudes_view, name='lista_solicitudes'),
    path('emp/', views.empleado_view, name='vista_empleado'), 
    path('responder/<int:solicitud_id>/', views.responer_solicitudes_view, name='responder_solicitudes'),
    path('nueva/', views.crear_solicitud_view, name='crear_solicitud'), 
    path('editar/<int:solicitud_id>/', views.editar_solicitud_view, name='editar_solicitud'),
    path('eliminar/<int:solicitud_id>/', views.eliminar_solicitud_view, name='eliminar_solicitud'),
    path('documento/<int:adjunto_id>/', views.descargar_adjunto_view, name='descargar_adjunto'),
    path('eliminar-adjunto/<int:adjunto_id>/', views.eliminar_adjunto_ajax, name='eliminar_adjunto_ajax'),
]