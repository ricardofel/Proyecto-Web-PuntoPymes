from django.db.models import Avg
from django.contrib.auth import get_user_model
from empleados.models import Empleado
from kpi.constants import CodigosKPI

def calcular_valor_automatico(kpi):
    """
    Calculadora basada en CÓDIGO, no en nombre.
    """
    empresa = kpi.empresa
    codigo = kpi.codigo

    if codigo == CodigosKPI.HEADCOUNT:
        return Empleado.objects.filter(
            empresa=empresa, 
            estado=Empleado.Estado.ACTIVO
        ).count()

    elif codigo == CodigosKPI.PUNTUALIDAD:
        # Lógica placeholder (aquí conectarías con módulo asistencia)
        return 95.0 

    elif codigo == CodigosKPI.AUSENTISMO:
        # Lógica placeholder
        return 2.5

    elif codigo == CodigosKPI.SALARIO_PROM:
        # CORRECCIÓN IMPORTANTE:
        # El campo 'salario' no existe en Empleado. Está dentro de la relación 'contratos'.
        # Usamos 'contratos__salario' para acceder al campo en la tabla relacionada.
        
        promedio = Empleado.objects.filter(
            empresa=empresa, 
            estado=Empleado.Estado.ACTIVO,
            # Opcional: Si tus contratos tienen estado, podrías filtrar: 
            # contratos__estado='activo'
            contratos__isnull=False # Solo empleados con contrato
        ).aggregate(media=Avg('contratos__salario'))['media']
        
        return round(promedio, 2) if promedio else 0.0

    elif codigo == CodigosKPI.MANUAL:
        # Si es manual, no calculamos nada, retornamos el último valor o 0
        ultimo = kpi.resultados.order_by('-periodo').first()
        return ultimo.valor if ultimo else 0.0

    return 0.0