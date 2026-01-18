from django.contrib import admin
from .models import Turno, EventoAsistencia, JornadaCalculada

# configuración de turnos
@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'hora_inicio', 'hora_fin', 'tolerancia_minutos', 'empresa', 'estado')
    list_filter = ('estado', 'empresa')
    search_fields = ('nombre',)

# configuración de eventos de asistencia
@admin.register(EventoAsistencia)
class EventoAsistenciaAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'tipo', 'registrado_el', 'origen', 'precision_gps')
    list_filter = ('tipo', 'registrado_el', 'origen', 'empleado__empresa')
    search_fields = ('empleado__nombres', 'empleado__apellidos')
    date_hierarchy = 'registrado_el'
    readonly_fields = ('registrado_el',)

# visualización de jornadas calculadas
@admin.register(JornadaCalculada)
class JornadaCalculadaAdmin(admin.ModelAdmin):
    list_display = (
        'empleado', 
        'fecha', 
        'hora_primera_entrada', 
        'hora_ultima_salida', 
        'minutos_tardanza', 
        'estado_coloreado'
    )
    list_filter = ('estado', 'fecha', 'empleado__empresa')
    search_fields = ('empleado__nombres', 'empleado__apellidos')
    date_hierarchy = 'fecha'

    # visualización de estado con color
    @admin.display(description='Estado')
    def estado_coloreado(self, obj):
        from django.utils.html import format_html
        
        colores = {
            'puntual': 'green',
            'atraso': 'orange',
            'falta': 'red',
            'permiso': 'blue',
            'incompleto': 'gray',
        }
        color = colores.get(obj.estado, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, 
            obj.get_estado_display()
        )