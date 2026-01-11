from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

# 1. IMPORTS DE TUS MODELOS (Según tus capturas)
from empleados.models import Puesto
from solicitudes.models import TipoAusencia  # Ojo: En tu modelo se llama TipoAusencia, no TipoSolicitud

# 2. IMPORTS DE LOS FORMULARIOS (Los que agregamos en el Paso 1 en core/forms.py)
from core.forms import PuestoForm, TipoAusenciaForm

# =========================================================
# VISTA PRINCIPAL: PANEL DE CONFIGURACIÓN
# =========================================================
@login_required
def gestion_configuracion_view(request):
    """
    Muestra la lista de Puestos y Tipos de Ausencia filtrados por la empresa actual.
    """
    # Recuperamos la empresa del Middleware
    empresa = getattr(request, 'empresa_actual', None)
    
    if not empresa:
        messages.error(request, "No hay una empresa seleccionada en el entorno.")
        return redirect('organizacion')

    # 1. FILTRAR DATOS (Solo de esta empresa)
    puestos = Puesto.objects.filter(empresa=empresa, estado=True).order_by('nombre')
    tipos_ausencia = TipoAusencia.objects.filter(empresa=empresa, estado=True).order_by('nombre')

    # 2. FORMULARIOS VACÍOS (Para los modales de creación)
    form_puesto = PuestoForm()
    form_ausencia = TipoAusenciaForm()

    context = {
        'puestos': puestos,
        'tipos_ausencia': tipos_ausencia,
        'form_puesto': form_puesto,
        'form_ausencia': form_ausencia,
        'empresa_actual': empresa
    }
    
    # Renderizamos el HTML que creamos en el Paso 4
    return render(request, 'core/organizacion/gestion_configuracion.html', context)

# =========================================================
# PROCESO: CREAR PUESTO
# =========================================================
@login_required
@require_POST
def crear_puesto_view(request):
    empresa = getattr(request, 'empresa_actual', None)
    if not empresa:
        messages.error(request, "Error de entorno: Sin empresa.")
        return redirect('configuracion_empresa')

    form = PuestoForm(request.POST)
    
    if form.is_valid():
        try:
            # commit=False para no guardar todavía
            puesto = form.save(commit=False)
            # ASIGNACIÓN FORZOSA DE LA EMPRESA
            puesto.empresa = empresa
            puesto.save()
            messages.success(request, f"Puesto '{puesto.nombre}' creado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al guardar: {e}")
    else:
        # Si hay error, mostramos el primero que encuentre
        first_error = next(iter(form.errors.values()))[0]
        messages.error(request, f"Error en el formulario: {first_error}")
    
    return redirect('configuracion_empresa')

# =========================================================
# PROCESO: CREAR TIPO DE AUSENCIA (Solicitud)
# =========================================================
@login_required
@require_POST
def crear_tipo_ausencia_view(request):
    empresa = getattr(request, 'empresa_actual', None)
    if not empresa:
        messages.error(request, "Error de entorno: Sin empresa.")
        return redirect('configuracion_empresa')

    form = TipoAusenciaForm(request.POST)
    
    if form.is_valid():
        try:
            tipo = form.save(commit=False)
            # ASIGNACIÓN FORZOSA DE LA EMPRESA
            tipo.empresa = empresa
            tipo.save()
            messages.success(request, f"Tipo '{tipo.nombre}' creado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al guardar: {e}")
    else:
        first_error = next(iter(form.errors.values()))[0]
        messages.error(request, f"Error en el formulario: {first_error}")
    
    return redirect('configuracion_empresa')