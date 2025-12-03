from django.urls import path
from core.views.auth_views import login_view, logout_view, dashboard_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("", dashboard_view, name="dashboard"),
]
