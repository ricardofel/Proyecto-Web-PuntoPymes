from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone 
from django.db.models import Sum, Avg

from kpi.models import KPI, KPIResultado
from kpi.forms import KPIForm, KPIResultadoForm
from empleados.models import Empleado, Contrato

def _empresa_actual(request):
    empresa = getattr(request, "empresa_actual", None)
    if empresa: return empresa
    empresa = getattr(request.user, "empresa", None)
    if empresa: return empresa
    return None

def _calcular_valor_automatico(kpi):
    """
    Calculadora Inteligente de KPIs.
    Si no hay datos reales, retorna 0.0 para no romper el flujo.
    """
    nombre = kpi.nombre.lower()
    empresa = kpi.empresa

    # 1. HEADCOUNT
    if "headcount" in nombre or "empleados" in nombre:
        return Empleado.objects.filter(empresa=empresa, estado=Empleado.Estado.ACTIVO).count()

    # 2. MASA SALARIAL
    elif "masa salarial" in nombre or "nómina" in nombre:
        total = Contrato.objects.filter(
            empresa=empresa, 
            estado=Contrato.Estado.VIGENTE
        ).aggregate(Sum('salario_base'))['salario_base__sum']
        return total if total else 0.00

    # 3. SALARIO PROMEDIO
    elif "salario promedio" in nombre:
        promedio = Contrato.objects.filter(
            empresa=empresa, 
            estado=Contrato.Estado.VIGENTE
        ).aggregate(Avg('salario_base'))['salario_base__avg']
        return round(promedio, 2) if promedio else 0.00

    # 4. PUNTUALIDAD (Simulación / Pendiente Conexión Asistencia)
    elif "puntualidad" in nombre:
        return 0.00 

    # 5. AUSENTISMO (Simulación / Pendiente Conexión Asistencia)
    elif "ausentismo" in nombre:
        return 0.00

    return 0.00

@login_required
def dashboard_view(request):
    empresa = _empresa_actual(request)
    kpis = KPI.objects.filter(empresa=empresa, estado=True).order_by("-id")
    
    for k in kpis:
        # CORRECCIÓN: .first() trae el registro más nuevo
        k.ultimo_resultado = k.resultados.order_by("-periodo").first()
        k.color_estado = "gray"
        
        if k.ultimo_resultado and k.meta_default:
            if k.ultimo_resultado.valor >= k.meta_default:
                k.color_estado = "green"
            else:
                k.color_estado = "red"

    return render(request, "kpi/dashboard.html", {
        "kpis": kpis,
        "form": KPIForm()
    })

@login_required
def kpi_crear_view(request):
    empresa = _empresa_actual(request)
    if request.method == "POST":
        form = KPIForm(request.POST)
        if form.is_valid():
            kpi = form.save(commit=False)
            kpi.empresa = empresa
            kpi.save()
            messages.success(request, "Indicador creado correctamente.")
            return redirect("kpi:dashboard")
    return HttpResponseBadRequest("Error en el formulario")

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
    resultados = kpi.resultados.order_by("-periodo")

    if request.method == "POST":
        form = KPIResultadoForm(request.POST)
        if form.is_valid():
            res = form.save(commit=False)
            res.kpi = kpi
            res.save()
            messages.success(request, f"Medición guardada.")
            return redirect("kpi:kpi_detalle", pk=pk)
    else:
        hoy = timezone.now().strftime("%Y-%m")
        form = KPIResultadoForm(initial={"periodo": hoy})

    return render(request, "kpi/kpi_detalle.html", {
        "kpi": kpi, "resultados": resultados, "form": form
    })

@login_required
def kpi_recalcular_view(request, pk: int):
    empresa = _empresa_actual(request)
    kpi = get_object_or_404(KPI, pk=pk, empresa=empresa)
    
    valor_calculado = _calcular_valor_automatico(kpi)
    
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