from django.urls import path
from . import views

urlpatterns = [
    path('reporte/', views.reporte_view, name="reporte"),
]
