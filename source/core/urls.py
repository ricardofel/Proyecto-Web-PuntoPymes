from django.urls import path, include
from core.views.auth_views import login_view, logout_view, dashboard_view
from .views import home_views, auth_views, organization_views
from usuarios.views import usuarios_views

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("password-change/", auth_views.password_change_view, name="password_change"),
    path("", dashboard_view, name="dashboard"),
    path("organizacion/", organization_views.organizacion_view, name="organizacion"),
    path("usuarios/", include("usuarios.urls")),
    path("poa/", include(("poa.urls", "poa"), namespace="poa")),
    path('asistencia/', include('asistencia.urls')),
]
