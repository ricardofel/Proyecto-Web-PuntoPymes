from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import KPIViewSet, KPIResultadoViewSet

# El Router crea las rutas automáticas (GET, POST, PUT, DELETE)
router = DefaultRouter()
router.register(r'kpis', KPIViewSet)
router.register(r'kpi-resultados', KPIResultadoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]