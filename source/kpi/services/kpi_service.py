from django.utils import timezone
from django.db import transaction
from kpi.models import KPI, KPIResultado
from kpi.constants import CodigosKPI
from kpi.calculators import calcular_valor_automatico

class KPIService:
    
    @staticmethod
    def asegurar_defaults(empresa):
        # definición de kpis base del sistema
        defaults = [
            {
                "codigo": CodigosKPI.HEADCOUNT,
                "nombre": "Total Empleados",
                "unidad_medida": "Colaboradores",
                "frecuencia": "mensual",
                "meta_default": 0,
                "descripcion": "Número total de empleados activos."
            },
            {
                "codigo": CodigosKPI.AUSENTISMO,
                "nombre": "Ausentismo Laboral",
                "unidad_medida": "%",
                "frecuencia": "mensual",
                "meta_default": 5.0,
                "descripcion": "Porcentaje de ausencias respecto a días laborales."
            },
            {
                "codigo": CodigosKPI.ROTACION,
                "nombre": "Rotación de Personal",
                "unidad_medida": "%",
                "frecuencia": "mensual",
                "meta_default": 2.0,
                "descripcion": "Tasa de salida de empleados."
            },
            {
                "codigo": CodigosKPI.PUNTUALIDAD,
                "nombre": "Puntualidad",
                "unidad_medida": "%",
                "frecuencia": "mensual",
                "meta_default": 95.0,
                "descripcion": "Porcentaje de llegadas a tiempo."
            },
            {
                "codigo": CodigosKPI.SALARIO_PROM,
                "nombre": "Salario Promedio",
                "unidad_medida": "USD",
                "frecuencia": "mensual",
                "meta_default": 0,
                "descripcion": "Promedio de salarios brutos activos."
            },
        ]
        
        creados = 0
        for data in defaults:
            # creación o actualización de definiciones de kpi
            obj, created = KPI.objects.update_or_create(
                empresa=empresa,
                codigo=data["codigo"], 
                defaults={
                    "nombre": data["nombre"],
                    "unidad_medida": data["unidad_medida"],
                    "frecuencia": data["frecuencia"],
                    "meta_default": data["meta_default"],
                    "descripcion": data.get("descripcion", "")
                }
            )
            if created: creados += 1
        return creados

    @staticmethod
    def garantizar_resultados_actuales(empresa):
        # generación de resultados faltantes para el mes actual
        periodo = timezone.now().strftime("%Y-%m")
        
        kpis = KPI.objects.filter(empresa=empresa, estado=True).exclude(codigo=CodigosKPI.MANUAL)
        
        calculados = 0
        for kpi in kpis:
            existe = KPIResultado.objects.filter(kpi=kpi, periodo=periodo).exists()
            
            if not existe:
                valor = calcular_valor_automatico(kpi)
                KPIResultado.objects.create(
                    kpi=kpi,
                    periodo=periodo,
                    valor=valor,
                    calculado_automatico=True,
                    fecha_creacion=timezone.now()
                )
                calculados += 1
        return calculados

    @staticmethod
    def recalcular_todo(empresa):
        # actualización forzada de todos los kpis automáticos
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