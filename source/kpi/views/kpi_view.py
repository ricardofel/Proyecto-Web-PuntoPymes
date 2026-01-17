from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import OuterRef, Subquery
from django.utils import timezone

from kpi.models import KPI, KPIResultado
from kpi.forms import KPIForm
from kpi.services.kpi_service import KPIService
from kpi.calculators import calcular_valor_automatico # Para el recálculo individual

def _empresa_actual(request):
    return getattr(request.user, "empresa", None)

@login_required
def dashboard_view(request):
    """Vista principal optimizada para evitar N+1 queries"""
    empresa = _empresa_actual(request)
    
    # Aseguramos defaults (rápido)
    KPIService.asegurar_defaults(empresa)
    
    # Subquery optimizada para traer el último valor
    ultimo_valor_sq = KPIResultado.objects.filter(
        kpi=OuterRef('pk')
    ).order_by('-periodo').values('valor')[:1]

    kpis = KPI.objects.filter(empresa=empresa, estado=True).annotate(
        ultimo_valor=Subquery(ultimo_valor_sq)
    )

    # Semáforo de colores en memoria
    for k in kpis:
        k.color = "gray"
        if k.ultimo_valor is not None and k.meta_default:
            k.color = "green" if k.ultimo_valor >= k.meta_default else "red"

    return render(request, "kpi/dashboard.html", {
        "kpis": kpis,
        "form": KPIForm()
    })

@login_required
def kpi_recalcular_global_view(request):
    """Botón 'Recalcular Todo'"""
    empresa = _empresa_actual(request)
    n = KPIService.recalcular_todo(empresa)
    messages.success(request, f"Se actualizaron {n} indicadores.")
    return redirect("kpi:dashboard")

@login_required
def kpi_generar_default_view(request):
    """Fuerza la generación de defaults"""
    empresa = _empresa_actual(request)
    n = KPIService.asegurar_defaults(empresa)
    if n > 0:
        messages.success(request, f"Se crearon {n} KPIs por defecto.")
    else:
        messages.info(request, "Los KPIs por defecto ya existen.")
    return redirect("kpi:dashboard")

@login_required
def kpi_recalcular_view(request, pk):
    """Recalcula UN solo KPI"""
    kpi = get_object_or_404(KPI, pk=pk, empresa=_empresa_actual(request))
    
    # Lógica manual rápida (podríamos moverla al servicio también, pero es simple)
    valor = calcular_valor_automatico(kpi)
    periodo = timezone.now().strftime("%Y-%m")
    
    KPIResultado.objects.update_or_create(
        kpi=kpi,
        periodo=periodo,
        defaults={
            "valor": valor,
            "calculado_automatico": True,
            "fecha_creacion": timezone.now()
        }
    )
    messages.success(request, f"Indicador '{kpi.nombre}' actualizado.")
    return redirect("kpi:dashboard")

@login_required
def kpi_detalle_view(request, pk):
    kpi = get_object_or_404(KPI, pk=pk, empresa=_empresa_actual(request))
    # Historial de resultados
    resultados = kpi.resultados.all().order_by('-periodo')
    return render(request, "kpi/kpi_detalle.html", {"kpi": kpi, "resultados": resultados})

@login_required
def kpi_editar_view(request, pk):
    kpi = get_object_or_404(KPI, pk=pk, empresa=_empresa_actual(request))
    if request.method == 'POST':
        form = KPIForm(request.POST, instance=kpi)
        if form.is_valid():
            form.save()
            messages.success(request, "KPI actualizado.")
            return redirect("kpi:dashboard")
    else:
        form = KPIForm(instance=kpi)
    return render(request, "kpi/form_kpi.html", {"form": form, "titulo": "Editar KPI"})

@login_required
def kpi_eliminar_view(request, pk):
    kpi = get_object_or_404(KPI, pk=pk, empresa=_empresa_actual(request))
    if request.method == 'POST':
        kpi.estado = False # Soft delete
        kpi.save()
        messages.success(request, "KPI eliminado correctamente.")
        return redirect("kpi:dashboard")
    return render(request, "kpi/confirmar_eliminar.html", {"obj": kpi})