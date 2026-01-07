from django.urls import path
from . import views

app_name = 'asistencia'

urlpatterns = [
    path('dashboard/', views.dashboard_asistencia_view, name='dashboard'),
    path('dashboard/<int:empleado_id>/', views.dashboard_asistencia_view, name='dashboard_empleado'),
]