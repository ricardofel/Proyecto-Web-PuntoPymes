from rest_framework import routers
# Importamos el ViewSet
from empleados.api_views import EmpleadoViewSet

router = routers.DefaultRouter()

# Registramos la ruta 'empleados'. 
# Esto creará automáticamente URLs como: /api/empleados/ y /api/empleados/1/
router.register(r'empleados', EmpleadoViewSet)

urlpatterns = router.urls