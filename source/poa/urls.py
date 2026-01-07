from django.urls import path
from .views.poa_view import (
    poa_view,
    poa_dashboard_partial,
    objetivo_crear_view,
    objetivo_detalle_view,
    objetivo_metas_partial,
    meta_crear_view,
    # Nuevas vistas
    meta_editar_view,
    meta_eliminar_view,
    actividad_crear_view,
    actividad_editar_view,
    actividad_eliminar_view,
    actividad_estado_view,
    objetivo_editar_view,
    objetivo_eliminar_view,
)

app_name = "poa"

urlpatterns = [
    path("", poa_view, name="poa"),
    path("dashboard/", poa_dashboard_partial, name="dashboard"),
    
    # Objetivos
    path("objetivos/crear/", objetivo_crear_view, name="objetivo_crear"),
    path("objetivos/<int:pk>/", objetivo_detalle_view, name="objetivo_detalle"),
    
    # Metas
    path("objetivos/<int:pk>/metas/", objetivo_metas_partial, name="objetivo_metas"),
    path("objetivos/<int:pk>/metas/crear/", meta_crear_view, name="meta_crear"),
    # Rutas nuevas para Metas
    path("metas/<int:pk>/editar/", meta_editar_view, name="meta_editar"),
    path("metas/<int:pk>/eliminar/", meta_eliminar_view, name="meta_eliminar"),
    
    # Actividades
    path("metas/<int:pk>/actividades/crear/", actividad_crear_view, name="actividad_crear"),
    # Rutas nuevas para Actividades
    path("actividades/<int:pk>/editar/", actividad_editar_view, name="actividad_editar"),
    path("actividades/<int:pk>/eliminar/", actividad_eliminar_view, name="actividad_eliminar"),
    path("actividades/<int:pk>/estado/", actividad_estado_view, name="actividad_estado"),
    path("objetivos/<int:pk>/editar/", objetivo_editar_view, name="objetivo_editar"),
    path("objetivos/<int:pk>/eliminar/", objetivo_eliminar_view, name="objetivo_eliminar"),

]