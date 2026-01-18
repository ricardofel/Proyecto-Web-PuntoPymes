from django.contrib import admin
from .models import IntegracionErp, Webhook, LogIntegracion


@admin.register(IntegracionErp)
class IntegracionAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Integraciones ERP.
    Permite gestionar conexiones con sistemas externos.
    """
    list_display = (
        'nombre',
        'url_api',
        'activo',
        'fecha_ultima_sincronizacion',
    )
    list_filter = ('activo', 'estado_sincronizacion')
    search_fields = ('nombre', 'url_api')


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Webhooks.
    Define eventos del sistema que disparan llamadas externas.
    """
    list_display = (
        'nombre',
        'evento',
        'url_destino',
        'activo',
    )
    list_filter = ('evento', 'activo')


@admin.register(LogIntegracion)
class LogIntegracionAdmin(admin.ModelAdmin):
    """
    Vista de solo lectura para el historial de integraciones.
    Sirve como auditoría técnica de llamadas externas.
    """
    list_display = (
        'fecha',
        'codigo_respuesta',
        'endpoint',
        'integracion',
        'webhook',
    )
    list_filter = ('codigo_respuesta', 'fecha')

    # Campos bloqueados para evitar alteración del historial
    readonly_fields = (
        'fecha',
        'codigo_respuesta',
        'mensaje_respuesta',
    )
