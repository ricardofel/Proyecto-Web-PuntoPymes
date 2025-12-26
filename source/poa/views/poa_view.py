from datetime import date

from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.db.models import Count

from poa.forms import ObjetivoForm
from poa.models import Objetivo


def _anio_actual_from_request(request) -> int:
    """
    Lee el año desde GET/POST. Si no viene, usa el año actual.
    """
    raw = request.GET.get("anio") or request.POST.get("anio")
    if raw:
        try:
            return int(raw)
        except ValueError:
            return date.today().year
    return date.today().year


def _build_dashboard_context(request, anio: int):
    """
    Construye el contexto del dashboard (stats + objetivos) para:
    - vista normal
    - partial HTMX
    - respuesta tras crear objetivo
    """
    q = (request.GET.get("q") or "").strip()
    estado = (request.GET.get("estado") or "").strip()

    qs = Objetivo.objects.filter(anio=anio)

    # Si tu app es multiempresa (lo es), idealmente filtra por empresa actual.
    # Ajusta según tu proyecto:
    # - request.empresa_actual (si usas middleware)
    # - request.user.empresa
    empresa = getattr(request, "empresa_actual", None) or getattr(
        request.user, "empresa", None
    )
    if empresa is not None:
        qs = qs.filter(empresa=empresa)

    if q:
        qs = qs.filter(nombre__icontains=q)

    if estado:
        qs = qs.filter(estado=estado)

    # Si aún no calculas avance real desde metas, deja 0.
    # Luego lo puedes reemplazar por un cálculo basado en metas/actividades.
    objetivos = qs.order_by("-fecha_creacion")

    stats = {
        "objetivos": objetivos.count(),
        "metas": 0,
        "actividades": 0,
        "avance_global": 0,
    }

    context = {
        "anio_actual": anio,
        "objetivos": objetivos,
        "stats": stats,
        "q": q,
        "filtro_estado": estado,
    }
    return context


def poa_view(request):
    """
    Página completa POA (cards + filtros + modal).
    El contenido de cards/stats se renderiza desde un include (dashboard_cards.html),
    y HTMX actualiza SOLO el contenedor #poa-dashboard.
    """
    anio = _anio_actual_from_request(request)

    # Lista de años (ajusta a tu gusto)
    anios = list(range(anio - 2, anio + 1))

    context = {
        "anio_actual": anio,
        "anios": anios,
        "form": ObjetivoForm(),  # IMPORTANTÍSIMO: el modal usa este form
    }

    # Si quieres renderizar el dashboard inicial desde el server, puedes pasar stats/objetivos aquí también,
    # pero como ya haces include del partial, suele bastar con que el include reciba data.
    # Para evitar "None" en el primer render, lo incluimos:
    context.update(_build_dashboard_context(request, anio))

    return render(request, "poa/poa.html", context)


def poa_dashboard_partial(request):
    """
    Partial HTMX: devuelve SOLO el contenido del dashboard (stats + cards)
    para insertarse dentro de #poa-dashboard.
    """
    anio = _anio_actual_from_request(request)
    context = _build_dashboard_context(request, anio)
    return render(request, "poa/partials/dashboard_cards.html", context)


def objetivo_crear_view(request):
    """
    POST HTMX desde el modal:
    - valida ObjetivoForm
    - crea objetivo con empresa + año
    - retorna el dashboard partial actualizado
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    anio = _anio_actual_from_request(request)

    form = ObjetivoForm(request.POST)
    if form.is_valid():
        objetivo = form.save(commit=False)
        objetivo.anio = anio

        empresa = getattr(request, "empresa_actual", None) or getattr(
            request.user, "empresa", None
        )
        if empresa is None:
            # Si tu proyecto siempre debe tener empresa, esto te ayuda a detectar el fallo real.
            return HttpResponseBadRequest("No se pudo determinar la empresa actual.")

        objetivo.empresa = empresa
        objetivo.save()

        # Nota: asignación de responsables (objetivo_empleado) la haces en el detalle.
    else:
        # Si quieres, aquí podrías devolver errores dentro del modal.
        # Pero como tu target es #poa-dashboard, lo más simple es:
        # devolver dashboard sin cambios y luego mejoras esto.
        pass

    context = _build_dashboard_context(request, anio)
    return render(request, "poa/partials/dashboard_cards.html", context)


def objetivo_detalle_view(request, pk: int):
    """
    Detalle del objetivo (por ahora básico).
    Luego aquí metes metas, actividades, roles objetivo_empleado, etc.
    """
    empresa = getattr(request, "empresa_actual", None) or getattr(
        request.user, "empresa", None
    )

    objetivo = get_object_or_404(Objetivo, pk=pk)
    if empresa is not None and objetivo.empresa_id != getattr(empresa, "id", None):
        # Protección multiempresa simple
        return HttpResponseBadRequest("Objetivo no pertenece a la empresa actual.")

    context = {
        "objetivo": objetivo,
    }
    return render(request, "poa/objetivo_detalle.html", context)
