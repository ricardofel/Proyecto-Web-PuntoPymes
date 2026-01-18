from rest_framework import serializers
from kpi.models import KPI, KPIResultado

class KPISerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source='empresa.nombre_comercial', read_only=True)

    class Meta:
        model = KPI
        fields = '__all__'

class KPIResultadoSerializer(serializers.ModelSerializer):
    kpi_nombre = serializers.CharField(source='kpi.nombre', read_only=True)
    unidad_medida = serializers.CharField(source='kpi.unidad_medida', read_only=True)

    class Meta:
        model = KPIResultado
        fields = '__all__'