from django.utils import timezone
from django.db import transaction
from kpi.models import KPI, KPIResultado
from kpi.constants import CodigosKPI
from kpi.calculators import calcular_valor_automatico

class KPIService:
    
    @staticmethod
    def asegurar_defaults(empresa):
        """Crea los KPIs base si no existen."""
        defaults = [
            {
                "codigo": CodigosKPI.HEADCOUNT,
                "nombre": "Total Empleados",
                "unidad_medida": "Colaboradores",
                "frecuencia": "mensual",
                "meta_default": 0
            },
            {
                "codigo": CodigosKPI.SALARIO_PROM,
                "nombre": "Salario Promedio",
                "unidad_medida": "USD",
                "frecuencia": "mensual",
                "meta_default": 0
            },
            # ... otros ...
        ]
        
        creados = 0
        for data in defaults:
            obj, created = KPI.objects.get_or_create(
                empresa=empresa,
                codigo=data["codigo"], # Buscamos por código único
                defaults=data
            )
            if created: creados += 1
        return creados

    @staticmethod
    def recalcular_todo(empresa):
        """
        Recalcula todos los KPIs automáticos.
        """
        periodo = timezone.now().strftime("%Y-%m")
        kpis = KPI.objects.filter(empresa=empresa, estado=True).exclude(codigo=CodigosKPI.MANUAL)
        
        actualizados = 0
        for kpi in kpis:
            valor = calcular_valor_automatico(kpi)
            KPIResultado.objects.update_or_create(
                kpi=kpi,
                periodo=periodo,
                defaults={
                    "valor": valor,
                    "calculado_automatico": True,
                    "fecha_creacion": timezone.now()
                }
            )
            actualizados += 1
        return actualizados