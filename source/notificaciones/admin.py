from django.contrib import admin
from .models import Notificacion

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo', 'leido', 'fecha_creacion')
    list_filter = ('leido', 'tipo', 'fecha_creacion')
    search_fields = ('titulo', 'mensaje', 'usuario__email')
    list_editable = ('leido',)