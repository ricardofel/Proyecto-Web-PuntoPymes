from django.urls import path, include
from core.views.auth_views import login_view, logout_view, dashboard_view
from core.views import auth_views 
from core.views import organization_views 

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("password-change/", auth_views.password_change_view, name="password_change"),
    path("", dashboard_view, name="dashboard"),
    path('organizacion/', organization_views.organizacion_dashboard, name='organizacion'),
    path("usuarios/", include("usuarios.urls")),
    path("poa/", include(("poa.urls", "poa"), namespace="poa")),
    path('asistencia/', include('asistencia.urls')),
    path("kpi/", include("kpi.urls")),
    path('api/kpi/', include('kpi.api.urls')),
    path('api/usuarios/', include('usuarios.api.urls')),
    path('api/poa/', include('poa.api.urls')),
    path('integraciones/', include('integraciones.urls')),
    path('organizacion/crear/', organization_views.crear_unidad, name='crear_unidad'),
    path('organizacion/editar/<int:pk>/', organization_views.editar_unidad, name='editar_unidad'),
    path('auditoria/', include('auditoria.urls')),
    path('notificaciones/', include('notificaciones.urls')),
    ]
