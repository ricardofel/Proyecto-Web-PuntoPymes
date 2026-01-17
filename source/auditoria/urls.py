from django.urls import path
from auditoria.views.auditoria_view import auditoria_dashboard_view

app_name = "auditoria"

urlpatterns = [
    path("", auditoria_dashboard_view, name="dashboard"),
]
