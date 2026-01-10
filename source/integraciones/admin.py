from django.contrib import admin
from .models import IntegracionErp, Webhook, LogIntegracion

@admin.register(IntegracionErp)
class IntegracionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'url_api', 'activo', 'fecha_ultima_sincronizacion')
    list_filter = ('activo', 'estado_sincronizacion')
    search_fields = ('nombre', 'url_api')

@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'evento', 'url_destino', 'activo')
    list_filter = ('evento', 'activo')

@admin.register(LogIntegracion)
class LogIntegracionAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'codigo_respuesta', 'endpoint', 'integracion', 'webhook')
    list_filter = ('codigo_respuesta', 'fecha')
    readonly_fields = ('fecha', 'codigo_respuesta', 'mensaje_respuesta')