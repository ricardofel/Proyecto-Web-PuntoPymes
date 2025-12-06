from django.contrib import admin
from .models import Turno

# Registramos SOLO el Turno (que es el modelo que me mostraste y que está bien)
@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    # Estos campos son idénticos a los de tu models.py
    list_display = ('nombre', 'hora_inicio', 'hora_fin', 'empresa', 'estado')
    
    # Filtros para la barra lateral derecha
    list_filter = ('estado', 'empresa')
    
    # Barra de búsqueda por nombre
    search_fields = ('nombre',)