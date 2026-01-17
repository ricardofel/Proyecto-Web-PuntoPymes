from django.contrib import admin
from .models import Empleado, Puesto, Contrato

@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):
    """
    Configuración de la interfaz administrativa para el modelo Puesto.
    Permite gestionar los cargos disponibles en la organización.
    """
    # Define las columnas que se mostrarán en la tabla de lista de registros.
    list_display = ('nombre', 'empresa', 'nivel', 'estado')
    
    # Habilita una barra de búsqueda para localizar puestos por su nombre.
    search_fields = ('nombre',)


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    """
    Configuración avanzada para la gestión de Empleados.
    Centraliza la visualización de la ficha técnica del colaborador.
    """
    # Columnas informativas visibles en el grid principal.
    list_display = ('nombres', 'apellidos', 'puesto', 'unidad_org', 'estado')
    
    # Agrega un panel lateral de filtros para segmentar empleados rápidamente.
    list_filter = ('estado', 'empresa', 'unidad_org')
    
    # Configura los campos por los cuales se puede realizar una búsqueda (LIKE query).
    search_fields = ('nombres', 'apellidos', 'cedula', 'email')


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    """
    Administración del historial de vinculaciones laborales (Contratos).
    Permite auditar las condiciones contractuales de cada empleado.
    """
    # Muestra la relación con el empleado, tipo de contrato y vigencia.
    list_display = ('empleado', 'tipo', 'fecha_inicio', 'estado')