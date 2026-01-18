from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import OuterRef, Subquery
from django.utils import timezone

from kpi.models import KPI, KPIResultado
from kpi.forms import KPIForm
from kpi.services.kpi_service import KPIService
from kpi.calculators import calcular_valor_automatico
from kpi.constants import CodigosKPI

def _empresa_actual(request):
    """Helper para obtener la empresa del usuario actual."""
    return getattr(request.user, "empresa", None)

@login_required
def dashboard_view(request):
    """
    Vista principal del Dashboard de KPIs.
    Calcula automáticamente los valores del mes si faltan y muestra semáforos.
    """
    empresa = request.empresa_actual 
    
    if not empresa:
        messages.warning(request, "Por favor seleccione una empresa para ver el Dashboard.")
        return redirect("dashboard")
    
    # 1. Aseguramos que existan los KPIs base (Headcount, Ausentismo, etc.)
    KPIService.asegurar_defaults(empresa)
    
    # 2. GARANTIZAR CÁLCULOS: Revisa si falta algún cálculo de ESTE mes y lo genera.
    KPIService.garantizar_resultados_actuales(empresa)
    
    # 3. Consulta Optimizada: Traemos los KPIs con su último valor registrado
    ultimo_valor_sq = KPIResultado.objects.filter(
        kpi=OuterRef('pk')
    ).order_by('-periodo').values('valor')[:1]

    kpis = KPI.objects.filter(empresa=empresa, estado=True).annotate(
        ultimo_valor=Subquery(ultimo_valor_sq)
    )

    # 4. Lógica de colores (Semáforo) en memoria
    for k in kpis:
        k.color = "gray"
        val = k.ultimo_valor
        meta = k.meta_default
        
        if val is not None and meta is not None:
            # Lógica inversa para KPIs donde "menos es mejor"
            es_kpi_inverso = k.codigo in [CodigosKPI.ROTACION, CodigosKPI.AUSENTISMO]
            
            if es_kpi_inverso:
                k.color = "green" if val <= meta else "red"
            else:
                k.color = "green" if val >= meta else "red"

    return render(request, "kpi/dashboard.html", {
        "kpis": kpis,
        "form": KPIForm()
    })

@login_required
def kpi_recalcular_global_view(request):
    """Botón 'Recalcular Todo': Fuerza actualización de todos los KPIs del mes."""
    empresa = _empresa_actual(request)
    n = KPIService.recalcular_todo(empresa)
    messages.success(request, f"Se actualizaron {n} indicadores.")
    return redirect("kpi:dashboard")

@login_required
def kpi_generar_default_view(request):
    """Fuerza la generación de los KPIs por defecto si fueron borrados."""
    empresa = _empresa_actual(request)
    n = KPIService.asegurar_defaults(empresa)
    if n > 0:
        messages.success(request, f"Se crearon {n} KPIs por defecto.")
    else:
        messages.info(request, "Los KPIs por defecto ya existen.")
    return redirect("kpi:dashboard")

@login_required
def kpi_recalcular_view(request, pk):
    """Recalcula UN solo KPI específico."""
    kpi = get_object_or_404(KPI, pk=pk, empresa=_empresa_actual(request))
    
    # Calculamos el valor al instante
    valor = calcular_valor_automatico(kpi)
    periodo = timezone.now().strftime("%Y-%m")
    
    # Guardamos o actualizamos
    KPIResultado.objects.update_or_create(
        kpi=kpi,
        periodo=periodo,
        defaults={
            "valor": valor,
            "calculado_automatico": True,
            "fecha_creacion": timezone.now()
        }
    )
    messages.success(request, f"Indicador '{kpi.nombre}' actualizado: {valor} {kpi.unidad_medida}")
    return redirect("kpi:dashboard")

@login_required
def kpi_detalle_view(request, pk):
    """Ver historial y detalle de un KPI."""
    kpi = get_object_or_404(KPI, pk=pk, empresa=_empresa_actual(request))
    resultados = kpi.resultados.all().order_by('-periodo')
    return render(request, "kpi/kpi_detalle.html", {"kpi": kpi, "resultados": resultados})

@login_required
def kpi_editar_view(request, pk):
    """Editar configuración de un KPI (meta, nombre, etc)."""
    kpi = get_object_or_404(KPI, pk=pk, empresa=_empresa_actual(request))
    if request.method == 'POST':
        form = KPIForm(request.POST, instance=kpi)
        if form.is_valid():
            form.save()
            messages.success(request, "KPI actualizado correctamente.")
            return redirect("kpi:dashboard")
    else:
        form = KPIForm(instance=kpi)
    return render(request, "kpi/form_kpi.html", {"form": form, "titulo": "Editar KPI"})

@login_required
def kpi_eliminar_view(request, pk):
    """Soft-delete de un KPI."""
    kpi = get_object_or_404(KPI, pk=pk, empresa=_empresa_actual(request))
    if request.method == 'POST':
        kpi.estado = False # Soft delete
        kpi.save()
        messages.success(request, "KPI eliminado correctamente.")
        return redirect("kpi:dashboard")
    return render(request, "kpi/confirmar_eliminar.html", {"obj": kpi})