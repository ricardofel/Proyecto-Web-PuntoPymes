from django.urls import path, include
from django.conf import settings                # <--- IMPORTANTE PARA MEDIA
from django.conf.urls.static import static      # <--- IMPORTANTE PARA MEDIA

from core.views.auth_views import login_view, logout_view
from core.views import auth_views 
from core.views import organization_views 
from core.views.core_views import visor_universal
from core.views.home_views import dashboard_view
from core.views import organization_views, config_views

urlpatterns = [
    # Autenticación y Home
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("", dashboard_view, name="dashboard"),
    path("password-change/", auth_views.password_change_view, name="password_change"),

    # Organización
    path('organizacion/', organization_views.organizacion_dashboard, name='organizacion'),
    path('organizacion/crear/', organization_views.crear_unidad, name='crear_unidad'),
    path('organizacion/editar/<int:pk>/', organization_views.editar_unidad, name='editar_unidad'),

    # Apps Principales
    path("usuarios/", include("usuarios.urls")),
    path("poa/", include(("poa.urls", "poa"), namespace="poa")),
    path('asistencia/', include('asistencia.urls')),
    path("kpi/", include("kpi.urls")),
    path('integraciones/', include('integraciones.urls')),
    path('auditoria/', include('auditoria.urls')),
    path('notificaciones/', include('notificaciones.urls')),

    # APIs
    path('api/usuarios/', include('usuarios.api.urls')),
    path('api/poa/', include('poa.api.urls')),

    # Utilidades
    path('detalles/<str:app_label>/<str:model_name>/<int:pk>/', visor_universal, name='visor_universal'),

    # NUEVAS RUTAS DE CONFIGURACIÓN
    path('organizacion/configuracion/', config_views.gestion_configuracion_view, name='configuracion_empresa'),
    path('organizacion/puesto/crear/', config_views.crear_puesto_view, name='crear_puesto'),
    path('organizacion/solicitud/crear/', config_views.crear_tipo_ausencia_view, name='crear_tipo_ausencia'),
]

# === CONFIGURACIÓN PARA SERVIR IMÁGENES (MEDIA) EN DESARROLLO ===
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)