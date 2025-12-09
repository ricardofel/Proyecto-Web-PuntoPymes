from django.contrib import admin
from django.utils.translation import gettext_lazy as _
# Importamos todos los modelos
from .models import (
    TipoAusencia, 
    SolicitudAusencia, 
    AprobacionAusencia, 
    RegistroVacaciones
)


## 1. ⚙️ Configuración para TipoAusencia
@admin.register(TipoAusencia)
class TipoAusenciaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "empresa",
        "afecta_sueldo",
        "requiere_documento",
        "descuenta_vacaciones",
        "estado",
        "fecha_creacion",
    )
    list_filter = ("empresa", "afecta_sueldo", "estado")
    search_fields = ("nombre", "descripcion")
    list_display_links = ("nombre",)
    list_editable = ("estado", "afecta_sueldo", "requiere_documento", "descuenta_vacaciones")





## 2. 📅 Configuración para SolicitudAusencia
@admin.register(SolicitudAusencia)
class SolicitudAusenciaAdmin(admin.ModelAdmin):
    list_display = (
        "empleado",
        "ausencia",
        "fecha_inicio",
        "fecha_fin",
        "dias_habiles",
        "estado",
        "fecha_creacion",
    )
    fieldsets = (
        (None, {"fields": ("empresa", "empleado", "ausencia")}),
        (_("Periodo y Días"), {"fields": ("fecha_inicio", "fecha_fin", "dias_habiles")}),
        (_("Detalles y Estado"), {"fields": ("motivo", "adjunto_url", "estado")}),
    )
    list_filter = ("empresa", "estado", "ausencia", "fecha_inicio")
    search_fields = (
        "empleado__nombre",
        "ausencia__nombre",
        "motivo",
    )
    date_hierarchy = "fecha_creacion"
    list_editable = ("estado",)





## 3. 🧑‍⚖️ Configuración para AprobacionAusencia
@admin.register(AprobacionAusencia)
class AprobacionAusenciaAdmin(admin.ModelAdmin):
    list_display = (
        "solicitud",
        "aprobador",
        "accion", 
        "fecha_accion",
        "comentario",
    )
    # 📌 CAMBIO CLAVE: Eliminamos 'fecha_accion' de readonly_fields.
    # Ahora será editable y tendrá un valor por defecto gracias al cambio en models.py.
    # readonly_fields = ("fecha_accion",) 
    
    list_filter = ("accion", "aprobador", "fecha_accion")
    search_fields = (
        "solicitud__empleado__nombre",
        "comentario",
    )





## 4. 🏖️ Configuración para RegistroVacaciones
@admin.register(RegistroVacaciones)
class RegistroVacacionesAdmin(admin.ModelAdmin):
    list_display = (
        "empleado",
        "empresa",
        "periodo",
        "dias_asignados",
        "dias_tomados",
        "dias_disponibles",
        "fecha_actualizacion",
    )
    list_filter = ("empresa", "periodo")
    search_fields = ("empleado__nombre", "periodo")
    list_editable = ("dias_asignados", "dias_tomados")
    readonly_fields = ("dias_disponibles", "fecha_actualizacion")