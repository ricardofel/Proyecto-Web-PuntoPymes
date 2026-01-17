from decimal import Decimal  # <-- ASEGÚRATE QUE ESTÉ AL PRINCIPIO
from django.db.models import Avg
from empleados.models import Empleado
from kpi.constants import CodigosKPI

def calcular_valor_automatico(kpi):
    empresa = kpi.empresa
    codigo = kpi.codigo

    if codigo == CodigosKPI.HEADCOUNT:
        # Convertimos el count (int) a Decimal
        return Decimal(Empleado.objects.filter(
            empresa=empresa, 
            estado=Empleado.Estado.ACTIVO
        ).count())

    elif codigo == CodigosKPI.PUNTUALIDAD:
        return Decimal("95.00") 

    elif codigo == CodigosKPI.AUSENTISMO:
        return Decimal("2.50")

    elif codigo == CodigosKPI.SALARIO_PROM:
        promedio = Empleado.objects.filter(
            empresa=empresa, 
            estado=Empleado.Estado.ACTIVO,
            contratos__isnull=False 
        ).aggregate(media=Avg('contratos__salario'))['media']
        
        if promedio is not None:
            # Redondeo financiero estándar
            return Decimal(str(promedio)).quantize(Decimal("0.00"))
        return Decimal("0.00")

    elif codigo == CodigosKPI.MANUAL:
        ultimo = kpi.resultados.order_by('-periodo').first()
        return ultimo.valor if ultimo else Decimal("0.00")

    return Decimal("0.00")