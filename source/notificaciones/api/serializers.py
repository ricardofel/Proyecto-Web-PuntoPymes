from rest_framework import serializers
from django.contrib.humanize.templatetags.humanize import naturaltime
from notificaciones.models import Notificacion

class NotificacionSerializer(serializers.ModelSerializer):
    tiempo_transcurrido = serializers.SerializerMethodField()

    class Meta:
        model = Notificacion
        exclude = ['usuario']

    def get_tiempo_transcurrido(self, obj):
        return naturaltime(obj.fecha_creacion)