from django.contrib import admin
from .models import KPI, KPIResultado

@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'unidad_medida', 'frecuencia', 'meta_default', 'estado')
    list_filter = ('empresa', 'frecuencia', 'estado')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('estado', 'meta_default') # Para editar rápido sin entrar al detalle
    ordering = ('empresa', 'nombre')

@admin.register(KPIResultado)
class KPIResultadoAdmin(admin.ModelAdmin):
    list_display = ('kpi', 'periodo', 'valor', 'get_empleado', 'calculado_automatico', 'fecha_creacion')
    list_filter = ('kpi__empresa', 'periodo', 'calculado_automatico')
    search_fields = ('kpi__nombre', 'periodo', 'empleado__nombres', 'empleado__apellidos')
    date_hierarchy = 'fecha_creacion'
    
    # Helper para mostrar "Global" si no tiene empleado
    def get_empleado(self, obj):
        return obj.empleado if obj.empleado else "--- GLOBAL ---"
    get_empleado.short_description = "Empleado / Alcance"