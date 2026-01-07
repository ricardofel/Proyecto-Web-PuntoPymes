from rest_framework import serializers
from poa.models import Objetivo, MetaTactico, Actividad

class ActividadSerializer(serializers.ModelSerializer):
    # Mostramos el nombre de la meta a la que pertenece (útil para listas generales)
    meta_nombre = serializers.CharField(source='meta.nombre', read_only=True)

    class Meta:
        model = Actividad
        fields = '__all__'

class MetaTacticoSerializer(serializers.ModelSerializer):
    objetivo_nombre = serializers.CharField(source='objetivo.nombre', read_only=True)
    # Calculamos cuántas actividades tiene
    total_actividades = serializers.IntegerField(source='actividades.count', read_only=True)

    class Meta:
        model = MetaTactico
        fields = '__all__'

class ObjetivoSerializer(serializers.ModelSerializer):
    # ¡MAGIA! Este campo lee la propiedad @property 'avance' de tu modelo
    avance = serializers.IntegerField(read_only=True)
    
    # Contamos cuántas metas tiene asociadas
    total_metas = serializers.IntegerField(source='metas_tacticas.count', read_only=True)

    class Meta:
        model = Objetivo
        fields = '__all__'