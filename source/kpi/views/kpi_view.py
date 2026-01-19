from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import OuterRef, Subquery
from django.utils import timezone

from kpi.models import KPI, KPIResultado
from kpi.forms import KPIForm
from kpi.constants import CodigosKPI

@login_required
def dashboard_view(request):
    """
    Vista principal. Usa 'request.empresa_actual' proporcionado por el Middleware
    para respetar la empresa seleccionada en la sesión.
    """
    # IMPORTACIÓN TARDÍA
    from kpi.services.kpi_service import KPIService

    # CAMBIO CLAVE: Usamos la empresa de la sesión (Middleware), no la del usuario fijo.
    empresa = getattr(request, 'empresa_actual', None)
    
    if not empresa:
        messages.warning(request, "No hay una empresa seleccionada en esta sesión.")
        # Redirigir a home o selector de empresa si existe
        return redirect("core:home") 
    
    # 1. Asegurar Defaults (Crea Cargos, Nómina, etc. si no existen)
    KPIService.asegurar_defaults(empresa)
    
    # 2. Garantizar cálculos del mes actual
    KPIService.garantizar_resultados_actuales(empresa)
    
    # 3. Consulta de semáforos
    ultimo_valor_sq = KPIResultado.objects.filter(
        kpi=OuterRef('pk')
    ).order_by('-periodo').values('valor')[:1]

    kpis = KPI.objects.filter(empresa=empresa, estado=True).annotate(
        ultimo_valor=Subquery(ultimo_valor_sq)
    )

    for k in kpis:
        k.color = "gray"
        val = k.ultimo_valor
        meta = k.meta_default
        
        if val is not None and meta is not None:
            # Lógica inversa (ej: Ausentismo, mientras menos mejor)
            es_kpi_inverso = k.codigo in [CodigosKPI.AUSENTISMO]
            
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
    from kpi.services.kpi_service import KPIService
    
    empresa = getattr(request, 'empresa_actual', None)
    if not empresa:
        return redirect("kpi:dashboard")

    n = KPIService.recalcular_todo(empresa)
    messages.success(request, f"Se actualizaron {n} indicadores para {empresa.nombre_comercial}.")
    return redirect("kpi:dashboard")

@login_required
def kpi_generar_default_view(request):
    from kpi.services.kpi_service import KPIService
    
    empresa = getattr(request, 'empresa_actual', None)
    if not empresa:
        return redirect("kpi:dashboard")

    n = KPIService.asegurar_defaults(empresa)
    if n > 0:
        messages.success(request, f"Se crearon {n} KPIs por defecto.")
    else:
        messages.info(request, "Los KPIs ya están configurados.")
    return redirect("kpi:dashboard")

@login_required
def kpi_recalcular_view(request, pk):
    from kpi.calculators import calcular_valor_automatico
    
    empresa = getattr(request, 'empresa_actual', None)
    # Seguridad: Solo permitimos recalcular KPIs de la empresa en sesión
    kpi = get_object_or_404(KPI, pk=pk, empresa=empresa)
    
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
    messages.success(request, f"Actualizado: {kpi.nombre}")
    return redirect("kpi:dashboard")

# Las vistas de detalle, editar y eliminar siguen el mismo patrón de seguridad
@login_required
def kpi_detalle_view(request, pk):
    empresa = getattr(request, 'empresa_actual', None)
    kpi = get_object_or_404(KPI, pk=pk, empresa=empresa)
    resultados = kpi.resultados.all().order_by('-periodo')
    return render(request, "kpi/kpi_detalle.html", {"kpi": kpi, "resultados": resultados})

@login_required
def kpi_editar_view(request, pk):
    empresa = getattr(request, 'empresa_actual', None)
    kpi = get_object_or_404(KPI, pk=pk, empresa=empresa)
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
    empresa = getattr(request, 'empresa_actual', None)
    kpi = get_object_or_404(KPI, pk=pk, empresa=empresa)
    if request.method == 'POST':
        kpi.estado = False
        kpi.save()
        messages.success(request, "KPI eliminado.")
        return redirect("kpi:dashboard")
    return render(request, "kpi/confirmar_eliminar.html", {"obj": kpi})