from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import ObjetivoViewSet, MetaTacticoViewSet, ActividadViewSet

router = DefaultRouter()
router.register(r'objetivos', ObjetivoViewSet)
router.register(r'metas', MetaTacticoViewSet)
router.register(r'actividades', ActividadViewSet)

urlpatterns = [
    path('', include(router.urls)),
]