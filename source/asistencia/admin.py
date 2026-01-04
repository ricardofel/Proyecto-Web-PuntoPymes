from django.contrib import admin
from .models import Turno, EventoAsistencia, JornadaCalculada

# 1. Configuración de Turnos
@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'hora_inicio', 'hora_fin', 'tolerancia_minutos', 'empresa', 'estado')
    list_filter = ('estado', 'empresa')
    search_fields = ('nombre',)

# 2. Configuración de Eventos (Marcaciones GPS/Biométrico)
@admin.register(EventoAsistencia)
class EventoAsistenciaAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'tipo', 'registrado_el', 'origen', 'precision_gps')
    list_filter = ('tipo', 'registrado_el', 'origen', 'empleado__empresa')
    search_fields = ('empleado__nombres', 'empleado__apellidos')
    date_hierarchy = 'registrado_el'
    
    # Hacemos que sea solo lectura la fecha para no alterar auditoría fácilmente
    readonly_fields = ('registrado_el',)

# 3. Configuración de Jornada Calculada (Lo que alimenta el Dashboard)
@admin.register(JornadaCalculada)
class JornadaCalculadaAdmin(admin.ModelAdmin):
    list_display = (
        'empleado', 
        'fecha', 
        'hora_primera_entrada', 
        'hora_ultima_salida', 
        'minutos_tardanza', 
        'estado_coloreado' # Usamos una función para ver el estado bonito
    )
    list_filter = ('estado', 'fecha', 'empleado__empresa')
    search_fields = ('empleado__nombres', 'empleado__apellidos')
    date_hierarchy = 'fecha'

    # Función para mostrar el estado con etiquetas de color en el Admin
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