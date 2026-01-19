from django.utils import timezone
from kpi.models import KPI, KPIResultado
from kpi.constants import CodigosKPI

class KPIService:
    
    @staticmethod
    def asegurar_defaults(empresa):
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
            {
                "codigo": CodigosKPI.COSTO_NOMINA,
                "nombre": "Costo Nómina Total",
                "unidad_medida": "USD",
                "frecuencia": "mensual",
                "meta_default": 0,
                "descripcion": "Suma total de salarios brutos (Contratos activos)."
            },
            {
                "codigo": CodigosKPI.SOLICITUDES_PEND,
                "nombre": "Solicitudes Pendientes",
                "unidad_medida": "Tickets",
                "frecuencia": "mensual",
                "meta_default": 0,
                "descripcion": "Número de solicitudes de ausencia sin procesar."
            },
            # --- NUEVO DEFAULT SEGURO ---
            {
                "codigo": CodigosKPI.TOTAL_CARGOS,
                "nombre": "Cargos Definidos",
                "unidad_medida": "Puestos",
                "frecuencia": "mensual",
                "meta_default": 0, 
                "descripcion": "Cantidad de puestos de trabajo configurados."
            },
        ]
        
        creados = 0
        for data in defaults:
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
        from kpi.calculators import calcular_valor_automatico
        periodo = timezone.now().strftime("%Y-%m")
        kpis = KPI.objects.filter(empresa=empresa, estado=True).exclude(codigo=CodigosKPI.MANUAL)
        calculados = 0
        for kpi in kpis:
            if not KPIResultado.objects.filter(kpi=kpi, periodo=periodo).exists():
                valor = calcular_valor_automatico(kpi)
                KPIResultado.objects.create(
                    kpi=kpi, periodo=periodo, valor=valor,
                    calculado_automatico=True, fecha_creacion=timezone.now()
                )
                calculados += 1
        return calculados

    @staticmethod
    def recalcular_todo(empresa):
        from kpi.calculators import calcular_valor_automatico
        periodo = timezone.now().strftime("%Y-%m")
        kpis = KPI.objects.filter(empresa=empresa, estado=True).exclude(codigo=CodigosKPI.MANUAL)
        actualizados = 0
        for kpi in kpis:
            valor = calcular_valor_automatico(kpi)
            KPIResultado.objects.update_or_create(
                kpi=kpi, periodo=periodo,
                defaults={"valor": valor, "calculado_automatico": True, "fecha_creacion": timezone.now()}
            )
            actualizados += 1
        return actualizados