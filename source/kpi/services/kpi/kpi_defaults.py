# kpi/services.py
from django.utils import timezone
from kpi.models import KPI, KPIResultado
from kpi.calculators import calcular_valor_automatico

DEFAULT_KPIS = [
    {
        "nombre": "Empleados Activos",
        "unidad_medida": "Colaboradores",
        "frecuencia": "mensual",
        "meta_default": 1,
        "descripcion": "Cantidad de empleados activos en la empresa.",
    },
    {
        "nombre": "Empleados Inactivos",
        "unidad_medida": "Colaboradores",
        "frecuencia": "mensual",
        "meta_default": None,  # KPI informativa (sin semáforo)
        "descripcion": "Cantidad de empleados inactivos.",
    },
    {
        "nombre": "Total de Empleados",
        "unidad_medida": "Colaboradores",
        "frecuencia": "mensual",
        "meta_default": 1,
        "descripcion": "Cantidad total de empleados registrados.",
    },
    {
        "nombre": "Porcentaje de Empleados Activos",
        "unidad_medida": "%",
        "frecuencia": "mensual",
        "meta_default": 80,
        "descripcion": "Porcentaje de empleados activos respecto al total.",
    },
    {
        "nombre": "Usuarios Activos",
        "unidad_medida": "Usuarios",
        "frecuencia": "mensual",
        "meta_default": 1,
        "descripcion": "Cantidad de usuarios activos en el sistema.",
    },
    {
        "nombre": "Porcentaje de Empleados con Usuario",
        "unidad_medida": "%",
        "frecuencia": "mensual",
        "meta_default": 90,
        "descripcion": "Porcentaje de empleados que ya tienen cuenta de usuario.",
    },
    {
        "nombre": "Empleados sin Usuario",
        "unidad_medida": "Colaboradores",
        "frecuencia": "mensual",
        "meta_default": 0,  # meta 0 ES válida
        "descripcion": "Cantidad de empleados que aún no tienen usuario creado.",
    },
]


def ensure_default_kpis(empresa) -> int:
    """
    Garantiza que existan las KPIs base para una empresa.
    Retorna cuántas se crearon.
    """
    if not empresa:
        return 0

    creados = 0
    for data in DEFAULT_KPIS:
        _, created = KPI.objects.get_or_create(
            empresa=empresa,
            nombre=data["nombre"],
            defaults=data,
        )
        if created:
            creados += 1
    return creados
