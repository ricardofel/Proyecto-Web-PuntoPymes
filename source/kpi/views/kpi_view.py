from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone 
from django.db.models import Sum, Avg
from django.template.loader import render_to_string

from kpi.calculators import calcular_valor_automatico
from kpi.models import KPI, KPIResultado
from kpi.forms import KPIForm, KPIResultadoForm
from empleados.models import Empleado, Contrato
from kpi.services.kpi.kpi_defaults import ensure_default_kpis
from kpi.services.kpi.kpi_recalc import recalculate_all_kpis_for_empresa

import json

def _annotate_kpis(kpis):
    for k in kpis:
        k.ultimo_resultado = k.resultados.order_by("-periodo").first()
        k.color_estado = "gray"
        if k.ultimo_resultado and k.meta_default is not None:
            k.color_estado = "green" if k.ultimo_resultado.valor >= k.meta_default else "red"
    return kpis

def _render_kpi_oob_response(request, empresa, toast_msg="Operación exitosa"):
    kpis = KPI.objects.filter(empresa=empresa, estado=True).order_by("-id")
    kpis = _annotate_kpis(kpis)

    grid_html = render_to_string("kpi/partials/kpi_grid.html", {"kpis": kpis}, request=request)

    response = HttpResponse(f'<div hx-swap-oob="innerHTML:#kpi-grid">{grid_html}</div>')
    response["HX-Trigger"] = json.dumps({"close-modal": toast_msg})
    response["HX-Reswap"] = "none"
    return response

def _empresa_actual(request):
    empresa = getattr(request, "empresa_actual", None)
    if empresa: return empresa
    empresa = getattr(request.user, "empresa", None)
    if empresa: return empresa
    return None

from empleados.models import Empleado

from django.contrib.auth import get_user_model
from empleados.models import Empleado

User = get_user_model()

@login_required
def dashboard_view(request):
    empresa = _empresa_actual(request)
    ensure_default_kpis(empresa)
    recalculate_all_kpis_for_empresa(empresa) 
    kpis = KPI.objects.filter(empresa=empresa, estado=True).order_by("-id")
    
    periodo_actual = timezone.now().strftime("%Y-%m")

    for k in kpis:
        k.ultimo_resultado = (
            k.resultados.filter(periodo=periodo_actual).first()
            or k.resultados.order_by("-periodo").first()
        )

        k.color_estado = "gray"
        if k.ultimo_resultado is not None and k.meta_default is not None:
            k.color_estado = "green" if k.ultimo_resultado.valor >= k.meta_default else "red"


    return render(request, "kpi/dashboard.html", {
        "kpis": kpis,
        "form": KPIForm()
    })


"""
@login_required
def kpi_crear_view(request):
    empresa = _empresa_actual(request)
    if request.method == "POST":
        form = KPIForm(request.POST)
        if form.is_valid():
            kpi = form.save(commit=False)
            kpi.empresa = empresa
            kpi.save()
            if request.headers.get("HX-Request") == "true":
                return _render_kpi_oob_response(request, empresa, "Indicador creado correctamente.")

            messages.success(request, "Indicador creado correctamente.")
            return redirect("kpi:dashboard")

    return HttpResponseBadRequest("Error en el formulario")
"""

@login_required
def kpi_generar_default_view(request):
    empresa = _empresa_actual(request)
    if not empresa: return redirect("kpi:dashboard")

    defaults = [
        # 👇 ESTE ES EL QUE FALTABA
        {
            "nombre": "Total Empleados",
            "unidad_medida": "Colaboradores",
            "frecuencia": "mensual",
            "meta_default": 1.00,
            "descripcion": "Headcount: Cantidad de empleados activos en nómina."
        },
        {"nombre": "Puntualidad General", "unidad_medida": "%", "frecuencia": "mensual", "meta_default": 95.00, "descripcion": "Porcentaje de ingresos a tiempo."},
        {"nombre": "Ausentismo Laboral", "unidad_medida": "%", "frecuencia": "mensual", "meta_default": 2.00, "descripcion": "Horas perdidas por faltas."},
        {"nombre": "Salario Promedio", "unidad_medida": "USD", "frecuencia": "anual", "meta_default": 0.00, "descripcion": "Promedio de remuneración."}
    ]

    creados = 0
    for data in defaults:
        obj, created = KPI.objects.get_or_create(empresa=empresa, nombre=data["nombre"], defaults=data)
        if created: creados += 1

    if creados > 0: messages.success(request, f"¡Listo! {creados} indicadores generados.")
    else: messages.info(request, "Tus indicadores ya están al día.")

    return redirect("kpi:dashboard")

@login_required
def kpi_detalle_view(request, pk: int):
    empresa = _empresa_actual(request)
    kpi = get_object_or_404(KPI, pk=pk, empresa=empresa)

    valor_calculado = calcular_valor_automatico(kpi)

    try:
        valor_calculado = float(valor_calculado)
    except (TypeError, ValueError):
        valor_calculado = 0.0
    periodo_actual = timezone.now().strftime("%Y-%m")

    KPIResultado.objects.update_or_create(
        kpi=kpi,
        periodo=periodo_actual,
        defaults={
            "valor": valor_calculado,
            "calculado_automatico": True,
            "observacion": "Cálculo automático del sistema."
        }
    )

    resultados = kpi.resultados.order_by("-periodo")

    return render(request, "kpi/kpi_detalle.html", {
        "kpi": kpi, "resultados": resultados
    })


@login_required
def kpi_recalcular_view(request, pk: int):
    empresa = _empresa_actual(request)
    kpi = get_object_or_404(KPI, pk=pk, empresa=empresa)
    
    valor_calculado = calcular_valor_automatico(kpi)
    
    periodo_actual = timezone.now().strftime("%Y-%m")
    
    KPIResultado.objects.update_or_create(
        kpi=kpi,
        periodo=periodo_actual,
        defaults={
            'valor': valor_calculado,
            'calculado_automatico': True,
            'observacion': 'Cálculo automático del sistema.'
        }
    )
    
    if valor_calculado == 0:
        messages.warning(request, f"Se calculó 0.00 (Posible falta de datos).")
    else:
        messages.success(request, f"¡Recálculo exitoso! Valor: {valor_calculado}")
        
    return redirect("kpi:kpi_detalle", pk=pk)

@login_required
def kpi_editar_view(request, pk):
    empresa = _empresa_actual(request)
    kpi = get_object_or_404(KPI, pk=pk, empresa=empresa)
    
    if request.method == "POST":
        form = KPIForm(request.POST, instance=kpi)
        if form.is_valid():
            form.save()
            messages.success(request, "Indicador actualizado correctamente.")
            return redirect("kpi:kpi_detalle", pk=pk)
    else:
        # Reusamos el KPIForm que ya tienes estilizado
        form = KPIForm(instance=kpi)
    
    # Reusamos el modal, pero necesitamos una plantilla simple o renderizarlo en el dashboard
    # Para simplificar, lo mandamos al dashboard abriendo el modal con datos (avanzado) 
    # O creamos una vista simple. Haremos una vista simple de edición.
    return render(request, "kpi/form_kpi.html", {"form": form, "titulo": "Editar KPI"})

@login_required
def kpi_eliminar_view(request, pk):
    empresa = _empresa_actual(request)
    kpi = get_object_or_404(KPI, pk=pk, empresa=empresa)
    
    if request.method == "POST":
        kpi.delete()
        messages.success(request, "Indicador eliminado correctamente.")
        return redirect("kpi:dashboard")
        
    # Pantalla de confirmación simple
    return render(request, "kpi/confirmar_eliminar.html", {"kpi": kpi})