from django.contrib import admin
from auditoria.models import LogAuditoria

@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    # Columnas que verás en la lista
    list_display = ('fecha', 'usuario', 'accion', 'modulo', 'modelo', 'detalle')
    
    # Filtros laterales para buscar rápido
    list_filter = ('accion', 'modulo', 'fecha', 'usuario')
    
    # Barra de búsqueda
    search_fields = ('detalle', 'usuario__email', 'objeto_id')
    
    # Nadie debe poder modificar la historia (Solo lectura)
    readonly_fields = ('fecha', 'usuario', 'accion', 'modulo', 'modelo', 'objeto_id', 'detalle', 'ip_address')

    def has_add_permission(self, request):
        return False # No permitir crear logs falsos
    
    def has_change_permission(self, request, obj=None):
        return False # No permitir alterar la evidencia
    
    def has_delete_permission(self, request, obj=None):
        return False # No permitir borrar rastros