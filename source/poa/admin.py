from django.contrib import admin
from .models import (
    Objetivo,
    MetaTactico,
    Actividad,
    ObjetivoEmpleado,
    MetaEmpleado,
    ActividadEmpleado,
)


@admin.register(Objetivo)
class ObjetivoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "anio", "empresa", "estado", "avance", "fecha_creacion")
    list_filter = ("empresa", "anio", "estado")
    search_fields = ("nombre", "descripcion")
    date_hierarchy = "fecha_creacion"


@admin.register(MetaTactico)
class MetaTacticoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "objetivo",
        "estado",
        "valor_esperado",
        "valor_actual",
        "fecha_fin",
    )
    list_filter = ("estado", "fecha_fin", "objetivo__empresa")
    search_fields = ("nombre", "objetivo__nombre")


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "meta", "estado", "porcentaje_avance", "fecha_fin")
    list_filter = ("estado", "fecha_fin")
    search_fields = ("nombre", "meta__nombre")


# Tablas pivote (opcional, útil para debugging)
admin.site.register(ObjetivoEmpleado)
admin.site.register(MetaEmpleado)
admin.site.register(ActividadEmpleado)
