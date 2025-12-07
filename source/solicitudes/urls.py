from django.urls import path
from . import views

# El nombre del namespace para usar en el HTML (ej: solicitudes:lista)
app_name = 'solicitudes'

urlpatterns = [
    # Ruta principal del módulo
    path('', views.lista_solicitudes_view, name='lista_solicitudes'),
    path('responder/', views.responer_solicitudes_view, name='responder_solicitudes'),
    # path('crear/', views.crear_solicitud_view, name='crear_solicitud'), # Futuro
]   