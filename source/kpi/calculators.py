from decimal import Decimal
from django.db.models import Avg, Sum
from django.utils import timezone
from kpi.constants import CodigosKPI

def calcular_valor_automatico(kpi):
    # --- IMPORTACIONES LOCALES PARA EVITAR CICLOS ---
    from empleados.models import Empleado, Contrato, Puesto
    from asistencia.models import EventoAsistencia
    from solicitudes.models import SolicitudAusencia
    # ------------------------------------------------

    empresa = kpi.empresa
    codigo = kpi.codigo
    now = timezone.now()
    mes_actual = now.month
    anio_actual = now.year

    # 1. HEADCOUNT (Total Empleados Activos)
    if codigo == CodigosKPI.HEADCOUNT:
        return Decimal(Empleado.objects.filter(
            empresa=empresa, 
            estado=Empleado.Estado.ACTIVO
        ).count())

    # 2. PUNTUALIDAD (Entradas a tiempo vs Total Entradas)
    elif codigo == CodigosKPI.PUNTUALIDAD:
        marcaciones = EventoAsistencia.objects.filter(
            empleado__empresa=empresa,
            empleado__estado=Empleado.Estado.ACTIVO,
            tipo=EventoAsistencia.TipoEvento.CHECK_IN,
            registrado_el__year=anio_actual,
            registrado_el__month=mes_actual
        ).select_related('empleado')

        total_entradas = 0
        entradas_a_tiempo = 0

        for m in marcaciones:
            emp = m.empleado
            # Solo evaluamos si tiene horario configurado
            if emp.hora_entrada_teorica:
                total_entradas += 1
                # Convertimos a hora local para comparar correctamente
                hora_real = timezone.localtime(m.registrado_el).time()
                
                # Tolerancia 0: debe llegar antes o a la misma hora exacta
                if hora_real <= emp.hora_entrada_teorica:
                    entradas_a_tiempo += 1
        
        if total_entradas > 0:
            val = (Decimal(entradas_a_tiempo) / Decimal(total_entradas)) * 100
            return val.quantize(Decimal("0.00"))
        
        return Decimal("0.00")

    # 3. AUSENTISMO (Días perdidos vs Días teóricos)
    elif codigo == CodigosKPI.AUSENTISMO:
        dias_perdidos = SolicitudAusencia.objects.filter(
            empresa=empresa,
            estado=SolicitudAusencia.Estado.APROBADO,
            fecha_inicio__year=anio_actual,
            fecha_inicio__month=mes_actual
        ).aggregate(total=Sum('dias_habiles'))['total'] or 0

        headcount = Empleado.objects.filter(
            empresa=empresa, 
            estado=Empleado.Estado.ACTIVO
        ).count()
        
        # Estimación estándar: 22 días laborables por empleado
        dias_teoricos = Decimal(headcount) * Decimal("22")

        if dias_teoricos > 0:
            val = (Decimal(dias_perdidos) / dias_teoricos) * 100
            return val.quantize(Decimal("0.00"))
        
        return Decimal("0.00")

    # 4. SALARIO PROMEDIO (Contratos vigentes)
    elif codigo == CodigosKPI.SALARIO_PROM:
        promedio = Contrato.objects.filter(
            empleado__empresa=empresa,
            empleado__estado=Empleado.Estado.ACTIVO,
            estado=True
        ).aggregate(media=Avg('salario'))['media']
        
        if promedio:
            return Decimal(str(promedio)).quantize(Decimal("0.00"))
        return Decimal("0.00")

    # 5. COSTO NÓMINA (Suma salarios vigentes)
    elif codigo == CodigosKPI.COSTO_NOMINA:
        total = Contrato.objects.filter(
            empleado__empresa=empresa,
            empleado__estado=Empleado.Estado.ACTIVO,
            estado=True
        ).aggregate(suma=Sum('salario'))['suma']
        
        if total:
            return Decimal(str(total)).quantize(Decimal("0.00"))
        return Decimal("0.00")

    # 6. SOLICITUDES PENDIENTES
    elif codigo == CodigosKPI.SOLICITUDES_PEND:
        pendientes = SolicitudAusencia.objects.filter(
            empresa=empresa,
            estado=SolicitudAusencia.Estado.PENDIENTE
        ).count()
        return Decimal(pendientes)

    # 7. TOTAL CARGOS (Puestos definidos)
    elif codigo == CodigosKPI.TOTAL_CARGOS:
        cargos = Puesto.objects.filter(
            empresa=empresa,
            estado=True
        ).count()
        return Decimal(cargos)

    # 8. MANUAL
    elif codigo == CodigosKPI.MANUAL:
        ultimo = kpi.resultados.order_by('-periodo').first()
        return ultimo.valor if ultimo else Decimal("0.00")

    return Decimal("0.00")