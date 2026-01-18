from django.contrib import admin
from auditoria.models import LogAuditoria


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    # Columnas visibles en el listado
    list_display = ("fecha", "usuario", "accion", "modulo", "modelo", "detalle")

    # Filtros laterales
    list_filter = ("accion", "modulo", "fecha", "usuario")

    # Campos habilitados para búsqueda
    search_fields = ("detalle", "usuario__email", "objeto_id")

    # Campos de solo lectura para preservar la integridad del log
    readonly_fields = (
        "fecha",
        "usuario",
        "accion",
        "modulo",
        "modelo",
        "objeto_id",
        "detalle",
        "ip_address",
    )

    def has_add_permission(self, request):
        # Evita la creación manual de registros de auditoría
        return False

    def has_change_permission(self, request, obj=None):
        # Evita la modificación de registros existentes
        return False

    def has_delete_permission(self, request, obj=None):
        # Evita la eliminación de registros de auditoría
        return False
