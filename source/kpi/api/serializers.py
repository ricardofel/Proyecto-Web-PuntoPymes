from rest_framework import serializers
from kpi.models import KPI, KPIResultado

class KPISerializer(serializers.ModelSerializer):
    """
    serializador para la definición de indicadores clave de desempeño.
    """
    empresa_nombre = serializers.CharField(source='empresa.nombre_comercial', read_only=True)

    class Meta:
        model = KPI
        fields = '__all__'

class KPIResultadoSerializer(serializers.ModelSerializer):
    """
    serializador para los valores históricos/mensuales de cada kpi.
    """
    # mostramos el nombre del kpi y su unidad para dar contexto al valor
    kpi_nombre = serializers.CharField(source='kpi.nombre', read_only=True)
    unidad_medida = serializers.CharField(source='kpi.unidad_medida', read_only=True)

    class Meta:
        model = KPIResultado
        fields = '__all__'