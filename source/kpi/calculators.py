# kpi/calculators.py
from django.contrib.auth import get_user_model
from empleados.models import Empleado

User = get_user_model()

def calcular_valor_automatico(kpi):
    """
    Calculadora automática basada en datos existentes del sistema.
    Siempre retorna un número (float o int).
    """
    nombre = (kpi.nombre or "").lower()
    empresa = kpi.empresa

    # 1) Empleados Activos
    if "empleados activos" in nombre:
        return Empleado.objects.filter(
            empresa=empresa,
            estado=Empleado.Estado.ACTIVO
        ).count()

    # 2) Empleados Inactivos
    elif "empleados inactivos" in nombre:
        return Empleado.objects.filter(
            empresa=empresa,
            estado=Empleado.Estado.INACTIVO
        ).count()

    # 3) Total de Empleados
    elif "total de empleados" in nombre or "total empleados" in nombre:
        return Empleado.objects.filter(empresa=empresa).count()

    # 4) % Empleados Activos
    elif "porcentaje de empleados activos" in nombre:
        total = Empleado.objects.filter(empresa=empresa).count()
        if total == 0:
            return 0.0
        activos = Empleado.objects.filter(
            empresa=empresa,
            estado=Empleado.Estado.ACTIVO
        ).count()
        return round((activos / total) * 100, 2)

    # 5) Usuarios Activos (tu User usa "estado")
    elif "usuarios activos" in nombre:
        return User.objects.filter(estado=True).count()

    # 6) % Empleados con Usuario (match flexible)
    elif "porcentaje" in nombre and "empleados" in nombre and "usuario" in nombre:
        total = Empleado.objects.filter(empresa=empresa).count()
        if total == 0:
            return 0.0
        con_usuario = Empleado.objects.filter(
            empresa=empresa,
            usuario__isnull=False
        ).count()
        return round((con_usuario / total) * 100, 2)

    # 7) Empleados sin Usuario (match flexible)
    elif "empleados" in nombre and "sin" in nombre and "usuario" in nombre:
        return Empleado.objects.filter(
            empresa=empresa,
            usuario__isnull=True
        ).count()

    # ✅ Default seguro: nunca devolver None
    return 0.0
