from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse

from .models import (
    TipoAusencia,
    SolicitudAusencia,
    AprobacionAusencia,
    RegistroVacaciones,
    AdjuntoSolicitud
)


class AdjuntoSolicitudInline(admin.TabularInline):
    """
    Inline para gestionar adjuntos de una solicitud desde el admin.
    Incluye enlace de descarga usando la ruta por ID de adjunto.
    """
    model = AdjuntoSolicitud
    extra = 0  # No muestra filas vacías adicionales
    fields = ('archivo', 'ver_documento', 'fecha_subida')
    readonly_fields = ('ver_documento', 'fecha_subida')

    def ver_documento(self, obj):
        # Link directo al endpoint de descarga del adjunto
        if obj.archivo:
            url = reverse('solicitudes:descargar_adjunto', args=[obj.id])
            return format_html(
                '<a class="button" href="{}" target="_blank" style="background-color: #4F46E5; color: white; padding: 4px 10px; border-radius: 4px; text-decoration: none;">Descargar PDF</a>',
                url
            )
        return "-"
    ver_documento.short_description = "Acción"


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


@admin.register(SolicitudAusencia)
class SolicitudAusenciaAdmin(admin.ModelAdmin):
    # Incluye contador de adjuntos como indicador rápido en la lista
    list_display = (
        "empleado",
        "ausencia",
        "fecha_inicio",
        "fecha_fin",
        "dias_habiles",
        "estado",
        "total_adjuntos",
        "fecha_creacion",
    )

    # Adjuntos visibles/editables dentro de la solicitud
    inlines = [AdjuntoSolicitudInline]

    fieldsets = (
        (None, {"fields": ("empresa", "empleado", "ausencia")}),
        (_("Periodo y Días"), {"fields": ("fecha_inicio", "fecha_fin", "dias_habiles")}),
        (_("Detalles y Estado"), {"fields": ("motivo", "estado")}),
    )

    list_filter = ("empresa", "estado", "ausencia", "fecha_inicio")

    search_fields = (
        "empleado__nombres",
        "empleado__apellidos",
        "ausencia__nombre",
        "motivo",
    )
    date_hierarchy = "fecha_creacion"
    list_editable = ("estado",)

    def total_adjuntos(self, obj):
        """
        Muestra cuántos archivos están asociados a la solicitud.
        """
        count = obj.adjuntos.count()
        if count > 0:
            return format_html('<strong style="color: #4F46E5;">{} archivos</strong>', count)
        return "Sin adjuntos"

    total_adjuntos.short_description = "Documentación"


@admin.register(AprobacionAusencia)
class AprobacionAusenciaAdmin(admin.ModelAdmin):
    list_display = (
        "solicitud",
        "aprobador",
        "accion",
        "fecha_accion",
        "comentario",
    )
    list_filter = ("accion", "aprobador", "fecha_accion")
    search_fields = (
        "solicitud__empleado__nombres",
        "comentario",
    )


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
    search_fields = ("empleado__nombres", "periodo")
    list_editable = ("dias_asignados", "dias_tomados")
    readonly_fields = ("dias_disponibles", "fecha_actualizacion")
