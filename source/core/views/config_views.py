from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from empleados.models import Puesto
from solicitudes.models import TipoAusencia

from core.forms import PuestoForm, TipoAusenciaForm


@login_required
def gestion_configuracion_view(request):
    """
    Panel de configuración.

    Lista puestos y tipos de ausencia asociados a la empresa actual
    (determinada por el middleware).
    """
    empresa = getattr(request, "empresa_actual", None)

    # Sin empresa activa no se permite operar en configuración.
    if not empresa:
        messages.error(request, "No hay una empresa seleccionada en el entorno.")
        return redirect("organizacion")

    # Datos filtrados por empresa (multitenencia).
    puestos = Puesto.objects.filter(empresa=empresa, estado=True).order_by("nombre")
    tipos_ausencia = TipoAusencia.objects.filter(empresa=empresa, estado=True).order_by("nombre")

    # Formularios vacíos para modales de creación.
    form_puesto = PuestoForm()
    form_ausencia = TipoAusenciaForm()

    context = {
        "puestos": puestos,
        "tipos_ausencia": tipos_ausencia,
        "form_puesto": form_puesto,
        "form_ausencia": form_ausencia,
        "empresa_actual": empresa,
    }

    return render(request, "core/organizacion/gestion_configuracion.html", context)


@login_required
@require_POST
def crear_puesto_view(request):
    """
    Crea un puesto para la empresa actual.
    """
    empresa = getattr(request, "empresa_actual", None)
    if not empresa:
        messages.error(request, "Error de entorno: Sin empresa.")
        return redirect("configuracion_empresa")

    form = PuestoForm(request.POST)

    if form.is_valid():
        try:
            puesto = form.save(commit=False)
            # Asignación controlada por servidor (evita crear registros fuera de la empresa activa).
            puesto.empresa = empresa
            puesto.save()
            messages.success(request, f"Puesto '{puesto.nombre}' creado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al guardar: {e}")
    else:
        # Mostrar un error representativo del formulario.
        first_error = next(iter(form.errors.values()))[0]
        messages.error(request, f"Error en el formulario: {first_error}")

    return redirect("configuracion_empresa")


@login_required
@require_POST
def crear_tipo_ausencia_view(request):
    """
    Crea un tipo de ausencia para la empresa actual.
    """
    empresa = getattr(request, "empresa_actual", None)
    if not empresa:
        messages.error(request, "Error de entorno: Sin empresa.")
        return redirect("configuracion_empresa")

    form = TipoAusenciaForm(request.POST)

    if form.is_valid():
        try:
            tipo = form.save(commit=False)
            # Asignación controlada por servidor (evita crear registros fuera de la empresa activa).
            tipo.empresa = empresa
            tipo.save()
            messages.success(request, f"Tipo '{tipo.nombre}' creado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al guardar: {e}")
    else:
        first_error = next(iter(form.errors.values()))[0]
        messages.error(request, f"Error en el formulario: {first_error}")

    return redirect("configuracion_empresa")
