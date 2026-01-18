from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.models import Empresa, UnidadOrganizacional
from core.forms import UnidadOrganizacionalForm


@login_required
def organizacion_dashboard(request):
    """
    Panel principal de Organización.

    Muestra las unidades de la empresa seleccionada a nivel global (request.empresa_actual),
    definida por el middleware.
    """

    # Empresa determinada por el middleware (selector global).
    empresa_actual = getattr(request, "empresa_actual", None)

    # Unidades asociadas a la empresa actual (si no hay empresa, se retorna vacío).
    if empresa_actual:
        unidades = (
            UnidadOrganizacional.objects.filter(empresa=empresa_actual)
            .select_related("padre")
            .order_by("nombre")
        )
    else:
        unidades = []

    # No es necesario pasar la lista completa de empresas: el selector vive en el layout/base.
    context = {
        "unidades": unidades,
        "empresa_actual": empresa_actual,
    }

    return render(request, "core/organizacion/panel_organizacion.html", context)


def crear_unidad(request):
    """
    Crear una nueva unidad organizacional para una empresa dada por querystring (?empresa_id=...).
    """
    empresa_id = request.GET.get("empresa_id")

    # Si no hay empresa, volver al panel (evita crear unidades sin contexto).
    if not empresa_id:
        return redirect("organizacion")

    empresa = get_object_or_404(Empresa, id=empresa_id)

    if request.method == "POST":
        form = UnidadOrganizacionalForm(request.POST, empresa_id=empresa_id)
        if form.is_valid():
            unidad = form.save(commit=False)
            unidad.empresa = empresa  # Asignación controlada por servidor.
            unidad.save()
            # Mantener el contexto de empresa al volver al panel.
            return redirect(f"/organizacion/?empresa_id={empresa_id}")
    else:
        form = UnidadOrganizacionalForm(empresa_id=empresa_id)

    context = {
        "form": form,
        "titulo": "Nueva Unidad Organizacional",
        "boton_texto": "Crear Unidad",
        "empresa": empresa,
    }
    return render(request, "core/organizacion/unidad_form.html", context)


def editar_unidad(request, pk):
    """
    Editar una unidad organizacional existente.
    """
    unidad = get_object_or_404(UnidadOrganizacional, pk=pk)
    empresa_id = unidad.empresa.id

    if request.method == "POST":
        form = UnidadOrganizacionalForm(request.POST, instance=unidad, empresa_id=empresa_id)
        if form.is_valid():
            form.save()
            return redirect(f"/organizacion/?empresa_id={empresa_id}")
    else:
        form = UnidadOrganizacionalForm(instance=unidad, empresa_id=empresa_id)

    context = {
        "form": form,
        "titulo": f"Editar: {unidad.nombre}",
        "boton_texto": "Guardar Cambios",
        "empresa": unidad.empresa,
    }
    return render(request, "core/organizacion/unidad_form.html", context)
