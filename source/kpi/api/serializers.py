from rest_framework import serializers
from kpi.models import KPI, KPIResultado
from empleados.models import Empleado

# --- EMPLEADO (Versión Ligera) ---
class EmpleadoSimpleSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Empleado
        fields = ['id', 'nombre_completo', 'cargo', 'departamento', 'estado']

    def get_nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellidos}"

# --- KPI (Definición) ---
class KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = '__all__'

# --- KPI RESULTADO (Datos) ---
class KPIResultadoSerializer(serializers.ModelSerializer):
    # Incluimos los detalles del empleado al leer, pero usamos ID para escribir
    empleado_info = EmpleadoSimpleSerializer(source='empleado', read_only=True)
    kpi_nombre = serializers.CharField(source='kpi.nombre', read_only=True)

    class Meta:
        model = KPIResultado
        fields = [
            'id', 'kpi', 'kpi_nombre', 'empleado', 'empleado_info',
            'periodo', 'valor', 'calculado_automatico', 
            'observacion', 'fecha_creacion'
        ]