from django.utils import timezone
from kpi.models import KPI, KPIResultado
from kpi.calculators import calcular_valor_automatico

def recalculate_all_kpis_for_empresa(empresa) -> int:
    if not empresa:
        return 0

    periodo_actual = timezone.now().strftime("%Y-%m")
    kpis = KPI.objects.filter(empresa=empresa, estado=True)

    updated = 0
    for kpi in kpis:
        valor = calcular_valor_automatico(kpi)

        # ✅ BLINDAJE: valor nunca puede ser None (tu DB es NOT NULL)
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            valor = 0.0

        KPIResultado.objects.update_or_create(
            kpi=kpi,
            periodo=periodo_actual,
            defaults={
                "valor": valor,
                "calculado_automatico": True,
                "observacion": "Cálculo automático del sistema."
            }
        )
        updated += 1

    return updated
