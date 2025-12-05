from django.urls import path
from core.views.auth_views import login_view, logout_view, dashboard_view
from .views import home_views, auth_views, organization_views

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("", dashboard_view, name="dashboard"),
    path('organizacion/', organization_views.organizacion_view, name='organizacion'),
]
