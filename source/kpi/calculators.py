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
        # Lógica placeholder (aquí conectarías con asistencia)
        return 95.0 

    elif codigo == CodigosKPI.AUSENTISMO:
        # Lógica placeholder
        return 2.5

    elif codigo == CodigosKPI.SALARIO_PROM:
        from django.db.models import Avg
        promedio = Empleado.objects.filter(
            empresa=empresa, 
            estado=Empleado.Estado.ACTIVO
        ).aggregate(Avg('salario'))['salario__avg']
        return round(promedio, 2) if promedio else 0.0

    elif codigo == CodigosKPI.MANUAL:
        # Si es manual, no calculamos nada, retornamos el último valor o 0
        ultimo = kpi.resultados.order_by('-periodo').first()
        return ultimo.valor if ultimo else 0.0

    return 0.0