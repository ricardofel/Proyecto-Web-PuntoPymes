from rest_framework import serializers
from django.contrib.humanize.templatetags.humanize import naturaltime
from notificaciones.models import Notificacion

class NotificacionSerializer(serializers.ModelSerializer):
    """
    Serializador para las alertas del sistema.
    Incluye formato de tiempo amigable (ej: 'hace 5 minutos').
    """
    tiempo_transcurrido = serializers.SerializerMethodField()

    class Meta:
        model = Notificacion
        exclude = ['usuario'] # No necesitamos enviar el ID del usuario al propio usuario

    def get_tiempo_transcurrido(self, obj):
        # Devuelve "hace 2 horas", "ayer", etc.
        return naturaltime(obj.fecha_creacion)