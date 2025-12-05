from django.contrib import admin
from .models import Empleado, Puesto, Contrato

@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'nivel', 'estado')
    search_fields = ('nombre',)

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'puesto', 'unidad_org', 'estado')
    list_filter = ('estado', 'empresa', 'unidad_org')
    search_fields = ('nombres', 'apellidos', 'cedula', 'email')

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'tipo', 'fecha_inicio', 'estado')