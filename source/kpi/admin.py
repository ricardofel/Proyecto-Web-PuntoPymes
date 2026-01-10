from django.contrib import admin
from .models import KPI, KPIResultado

class KPIResultadoInline(admin.TabularInline):
    model = KPIResultado
    extra = 0
    readonly_fields = ('fecha_creacion',)
    can_delete = True

@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'unidad_medida', 'frecuencia', 'meta_default', 'estado')
    list_filter = ('empresa', 'frecuencia', 'estado')
    search_fields = ('nombre', 'descripcion')
    inlines = [KPIResultadoInline] # ¡Esto permite ver los resultados dentro del KPI!

@admin.register(KPIResultado)
class KPIResultadoAdmin(admin.ModelAdmin):
    list_display = ('kpi', 'periodo', 'valor', 'calculado_automatico', 'fecha_creacion')
    list_filter = ('calculado_automatico', 'periodo', 'kpi__empresa')