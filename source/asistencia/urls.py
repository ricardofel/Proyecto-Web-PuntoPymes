from django.urls import path
from . import views

app_name = 'asistencia'

urlpatterns = [
    # 1. SEMÁFORO
    path('', views.asistencia_home_view, name='inicio'),

    # 2. PANTALLA DE BOTONES
    path('marcar/', views.zona_marcaje_view, name='zona_marcaje'),

    # 3. PANTALLA DE CALENDARIO
    path('dashboard/', views.dashboard_asistencia_view, name='dashboard'),

    # 4. PROCESAMIENTO
    path('registrar_marca/', views.registrar_marca_view, name='registrar_marca'),
    
    # 5. API AJAX (NUEVO)
    path('api/detalle-dia/', views.obtener_detalle_dia_view, name='api_detalle_dia'),
]