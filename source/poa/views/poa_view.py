from datetime import date
from decimal import Decimal
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse

from usuarios.decorators import solo_superusuario_o_admin_rrhh
from poa.forms import ObjetivoForm, MetaTacticoForm, ActividadForm
from poa.models import Objetivo, MetaTactico, Actividad


# --- UTILIDADES ---

def _anio_actual_from_request(request) -> int:
    """Obtiene el año del request (GET/POST) o devuelve el actual."""
    raw = request.GET.get("anio") or request.POST.get("anio")
    try:
        return int(raw) if raw else date.today().year
    except ValueError:
        return date.today().year


def _empresa_actual(request):
    """Obtiene la empresa del usuario actual de forma segura."""
    if hasattr(request, "empresa_actual") and request.empresa_actual:
        return request.empresa_actual

    user = request.user
    if getattr(user, "empresa", None):
        return user.empresa

    empleado = getattr(user, "empleado", None)
    if empleado:
        return getattr(empleado, "empresa", None)

    return None


def _verificar_permiso_empresa(request, objetivo):
    """Verifica si el objetivo pertenece a la empresa del usuario actual."""
    empresa = _empresa_actual(request)
    if empresa and objetivo.empresa_id != getattr(empresa, "id", None):
        return False
    return True


def _recalcular_avance_meta(meta: MetaTactico):
    """
    Recalcula el valor_actual de una meta basado en el % de actividades completadas.
    valor_esperado debe ser 100 y valor_actual 0..100 (por regla del proyecto).
    """
    total_actividades = meta.actividades.count()

    if total_actividades == 0:
        meta.valor_actual = Decimal("0.00")
    else:
        completadas = meta.actividades.filter(estado="completada").count()
        
        # --- REFACTORIZACIÓN PRIORIDAD 2: Estabilidad Matemática ---
        numerador = Decimal(completadas)
        denominador = Decimal(total_actividades)
        ratio = numerador / denominador
        
        # Convertimos explícitamente a Decimal, por si viene como float de algún lado
        valor_base = Decimal(str(meta.valor_esperado))
        
        meta.valor_actual = valor_base * ratio
        # -----------------------------------------------------------

    meta.save(update_fields=["valor_actual"])


def _build_dashboard_context(request, anio: int):
    """Construye el contexto para el dashboard principal."""
    q = (request.GET.get("q") or "").strip()
    estado = (request.GET.get("estado") or "").strip()
    empresa = _empresa_actual(request)

    qs = Objetivo.objects.filter(anio=anio)
    if empresa:
        qs = qs.filter(empresa=empresa)

    if q:
        qs = qs.filter(nombre__icontains=q)
    if estado:
        qs = qs.filter(estado=estado)

    objetivos_qs = qs.prefetch_related("metas_tacticas").order_by("-fecha_creacion")

    metas_count = MetaTactico.objects.filter(objetivo__in=objetivos_qs).count()
    actividades_count = Actividad.objects.filter(meta__objetivo__in=objetivos_qs).count()

    objetivos_list = list(objetivos_qs)

    if objetivos_list:
        total_avance = sum(o.avance for o in objetivos_list)
        avance_global = int(total_avance / len(objetivos_list))
    else:
        avance_global = 0

    stats = {
        "objetivos": len(objetivos_list),
        "metas": metas_count,
        "actividades": actividades_count,
        "avance_global": avance_global,
    }

    return {
        "anio_actual": anio,
        "objetivos": objetivos_list,
        "stats": stats,
        "q": q,
        "filtro_estado": estado,
    }


def _render_oob_response(request, objetivo=None, metas_qs=None, toast_msg="Operación exitosa"):
    """
    Respuesta robusta usando HX-Trigger. IMPORTANTE:
    Siempre pasamos empleado_actual al template meta_list.html,
    porque ahí decides si el user puede hacer toggle o no.
    """
    response_content = ""

    empleado_actual = getattr(request.user, "empleado", None)

    # 1) Actualizar contenedor de metas
    if metas_qs is not None:
        lista_html = render_to_string(
            "poa/partials/meta_list.html",
            {"metas": metas_qs, "empleado_actual": empleado_actual},
            request,
        )
        response_content += f'<div hx-swap-oob="innerHTML:#metas-container">{lista_html}</div>'

    # 2) Actualizar header del objetivo
    if objetivo is not None:
        header_html = render_to_string(
            "poa/partials/objetivo_header.html",
            {"objetivo": objetivo},
            request,
        )
        response_content += f'<div hx-swap-oob="innerHTML:#objetivo-header">{header_html}</div>'

    response = HttpResponse(response_content)

    # 3) Señal al frontend para cerrar modal + toast
    response["HX-Trigger"] = json.dumps({"close-modal": toast_msg})
    response["HX-Reswap"] = "none"
    return response


# --- VISTAS PRINCIPALES ---

@login_required
def poa_view(request):
    anio = _anio_actual_from_request(request)
    anios = list(range(anio - 2, anio + 2))
    context = {"anio_actual": anio, "anios": anios, "form": ObjetivoForm()}
    context.update(_build_dashboard_context(request, anio))
    return render(request, "poa/poa.html", context)


@login_required
def poa_dashboard_partial(request):
    anio = _anio_actual_from_request(request)
    context = _build_dashboard_context(request, anio)
    return render(request, "poa/partials/dashboard_cards.html", context)


@login_required
@solo_superusuario_o_admin_rrhh
def objetivo_crear_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    anio = _anio_actual_from_request(request)
    form = ObjetivoForm(request.POST)

    if form.is_valid():
        empresa = _empresa_actual(request)
        if not empresa:
            form.add_error(None, "No tienes una empresa asignada.")
        else:
            objetivo = form.save(commit=False)
            objetivo.anio = anio
            objetivo.empresa = empresa
            objetivo.save()
            form.save_m2m()

            context_dash = _build_dashboard_context(request, anio)
            dashboard_html = render_to_string("poa/partials/dashboard_cards.html", context_dash, request)

            response = HttpResponse(f'<div hx-swap-oob="innerHTML:#poa-dashboard">{dashboard_html}</div>')
            response["HX-Trigger"] = json.dumps({"close-modal": "Objetivo creado"})
            return response

    return render(request, "poa/partials/modal_objetivo.html", {"form": form, "anio_actual": anio})


@login_required
def objetivo_detalle_view(request, pk: int):
    objetivo = get_object_or_404(Objetivo, pk=pk)
    if not _verificar_permiso_empresa(request, objetivo):
        return HttpResponseBadRequest("Objetivo no pertenece a la empresa actual.")

    metas = MetaTactico.objects.filter(objetivo=objetivo).prefetch_related(
        "actividades",
        "actividades__ejecutores",
    ).order_by("-fecha_fin", "-id")

    empleado_actual = getattr(request.user, "empleado", None)

    return render(request, "poa/objetivo_detalle.html", {
        "objetivo": objetivo,
        "metas": metas,
        "meta_form": MetaTacticoForm(),
        "empleado_actual": empleado_actual,
    })


@login_required
def objetivo_metas_partial(request, pk: int):
    objetivo = get_object_or_404(Objetivo, pk=pk)
    if not _verificar_permiso_empresa(request, objetivo):
        return HttpResponseBadRequest("Objetivo no pertenece a la empresa actual.")

    metas = MetaTactico.objects.filter(objetivo=objetivo).prefetch_related(
        "actividades",
        "actividades__ejecutores",
    ).order_by("-fecha_fin", "-id")

    empleado_actual = getattr(request.user, "empleado", None)

    return render(request, "poa/partials/meta_list.html", {
        "objetivo": objetivo,
        "metas": metas,
        "empleado_actual": empleado_actual,
    })


# --- GESTIÓN DE OBJETIVOS ---

@login_required
@solo_superusuario_o_admin_rrhh
def objetivo_editar_view(request, pk: int):
    obj = get_object_or_404(Objetivo, pk=pk)
    if not _verificar_permiso_empresa(request, obj):
        return HttpResponseBadRequest("Sin permiso")

    if request.method == "POST":
        form = ObjetivoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()

            referer = request.META.get("HTTP_REFERER", "")
            response_content = ""

            if "objetivos/" in referer and "dashboard" not in referer:
                header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": obj}, request)
                response_content = f'<div hx-swap-oob="innerHTML:#objetivo-header">{header_html}</div>'
            else:
                anio = obj.anio
                context_dash = _build_dashboard_context(request, anio)
                dashboard_html = render_to_string("poa/partials/dashboard_cards.html", context_dash, request)
                response_content = f'<div hx-swap-oob="innerHTML:#poa-dashboard">{dashboard_html}</div>'

            response = HttpResponse(response_content)
            response["HX-Trigger"] = json.dumps({"close-modal": "Objetivo actualizado"})
            return response
    else:
        form = ObjetivoForm(instance=obj)

    return render(request, "poa/partials/modal_objetivo.html", {
        "form": form,
        "anio_actual": obj.anio,
        "is_edit": True,
        "edit_url": request.path
    })


@login_required
@solo_superusuario_o_admin_rrhh
def objetivo_eliminar_view(request, pk: int):
    obj = get_object_or_404(Objetivo, pk=pk)
    if not _verificar_permiso_empresa(request, obj):
        return HttpResponseBadRequest("Sin permiso")

    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    obj.delete()

    referer = request.META.get("HTTP_REFERER", "")
    if "objetivos/" in referer and "dashboard" not in referer:
        return HttpResponse(status=200, headers={"HX-Redirect": reverse("poa:poa")})

    anio = _anio_actual_from_request(request)
    context_dash = _build_dashboard_context(request, anio)
    dashboard_html = render_to_string("poa/partials/dashboard_cards.html", context_dash, request)

    return HttpResponse(
        f'<div hx-swap-oob="innerHTML:#poa-dashboard">{dashboard_html}</div>'
        f"<script>Swal.fire({{icon:'success', title:'Objetivo eliminado', toast:true, position:'top-end', showConfirmButton:false, timer:3000}});</script>"
    )


@login_required
@solo_superusuario_o_admin_rrhh
def cambiar_estado_objetivo(request, pk):
    objetivo = get_object_or_404(Objetivo, pk=pk)
    if not _verificar_permiso_empresa(request, objetivo):
        return HttpResponseBadRequest("Sin permiso")

    if objetivo.estado == "activo":
        objetivo.estado = "cerrado"
        messages.warning(request, f"El objetivo '{objetivo.nombre}' ha sido cerrado.")
    else:
        objetivo.estado = "activo"
        messages.success(request, f"El objetivo '{objetivo.nombre}' ahora está activo.")

    objetivo.save()
    return redirect("poa:objetivo_detalle", pk=pk)


# --- GESTIÓN DE METAS ---

@login_required
@solo_superusuario_o_admin_rrhh
def meta_crear_view(request, pk: int):
    objetivo = get_object_or_404(Objetivo, pk=pk)
    if not _verificar_permiso_empresa(request, objetivo):
        return HttpResponseBadRequest("No tiene permiso.")

    if request.method == "POST":
        form = MetaTacticoForm(request.POST)
        if form.is_valid():
            meta = form.save(commit=False)
            meta.objetivo = objetivo
            meta.save()
            form.save_m2m()

            metas = MetaTactico.objects.filter(objetivo=objetivo).prefetch_related(
                "actividades", "actividades__ejecutores"
            ).order_by("-fecha_fin", "-id")
            return _render_oob_response(request, objetivo, metas, "Meta creada")

        return render(request, "poa/partials/modal_meta.html", {"objetivo": objetivo, "meta_form": form})

    form = MetaTacticoForm()
    return render(request, "poa/partials/modal_meta.html", {"objetivo": objetivo, "meta_form": form})


@login_required
@solo_superusuario_o_admin_rrhh
def meta_editar_view(request, pk: int):
    meta = get_object_or_404(MetaTactico, pk=pk)
    if not _verificar_permiso_empresa(request, meta.objetivo):
        return HttpResponseBadRequest("Sin permiso")

    if request.method == "POST":
        form = MetaTacticoForm(request.POST, instance=meta)
        if form.is_valid():
            form.save()

            metas = MetaTactico.objects.filter(objetivo=meta.objetivo).prefetch_related(
                "actividades", "actividades__ejecutores"
            ).order_by("-fecha_fin", "-id")

            return _render_oob_response(request, meta.objetivo, metas, "Meta actualizada")
    else:
        form = MetaTacticoForm(instance=meta)

    return render(request, "poa/partials/modal_meta.html", {
        "objetivo": meta.objetivo,
        "meta_form": form,
        "is_edit": True,
        "edit_url": request.path,
    })


@login_required
@solo_superusuario_o_admin_rrhh
def meta_eliminar_view(request, pk: int):
    meta = get_object_or_404(MetaTactico, pk=pk)
    objetivo = meta.objetivo
    if not _verificar_permiso_empresa(request, objetivo):
        return HttpResponseBadRequest("No tiene permiso.")

    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    meta.delete()
    metas = MetaTactico.objects.filter(objetivo=objetivo).prefetch_related(
        "actividades", "actividades__ejecutores"
    ).order_by("-fecha_fin", "-id")

    return _render_oob_response(request, objetivo, metas, "Meta eliminada")


# --- GESTIÓN DE ACTIVIDADES ---

@login_required
@solo_superusuario_o_admin_rrhh
def actividad_crear_view(request, pk: int):
    meta = get_object_or_404(MetaTactico, pk=pk)
    if not _verificar_permiso_empresa(request, meta.objetivo):
        return HttpResponseBadRequest("No tiene permiso.")

    if request.method == "POST":
        form = ActividadForm(request.POST)
        if form.is_valid():
            actividad = form.save(commit=False)
            actividad.meta = meta
            actividad.save()
            form.save_m2m()  # guarda ejecutores

            _recalcular_avance_meta(meta)

            metas = MetaTactico.objects.filter(objetivo=meta.objetivo).prefetch_related(
                "actividades", "actividades__ejecutores"
            ).order_by("-fecha_fin", "-id")
            return _render_oob_response(request, meta.objetivo, metas, "Actividad creada")

        return render(request, "poa/partials/modal_actividad.html", {"form": form, "meta_id": pk, "meta_nombre": meta.nombre})

    return render(request, "poa/partials/modal_actividad.html", {
        "form": ActividadForm(),
        "meta_id": pk,
        "meta_nombre": meta.nombre,
    })


@login_required
@solo_superusuario_o_admin_rrhh
def actividad_editar_view(request, pk: int):
    act = get_object_or_404(Actividad, pk=pk)
    if not _verificar_permiso_empresa(request, act.meta.objetivo):
        return HttpResponseBadRequest("No tiene permiso.")

    if request.method == "POST":
        form = ActividadForm(request.POST, instance=act)
        if form.is_valid():
            form.save()
            _recalcular_avance_meta(act.meta)

            metas = MetaTactico.objects.filter(objetivo=act.meta.objetivo).prefetch_related(
                "actividades", "actividades__ejecutores"
            ).order_by("-fecha_fin", "-id")
            return _render_oob_response(request, act.meta.objetivo, metas, "Actividad actualizada")
    else:
        form = ActividadForm(instance=act)

    return render(request, "poa/partials/modal_actividad.html", {
        "form": form,
        "meta_id": act.meta.id,
        "meta_nombre": act.meta.nombre,
        "is_edit": True,
        "edit_url": request.path,
    })


@login_required
@solo_superusuario_o_admin_rrhh
def actividad_eliminar_view(request, pk: int):
    act = get_object_or_404(Actividad, pk=pk)
    meta = act.meta
    objetivo = meta.objetivo

    if not _verificar_permiso_empresa(request, objetivo):
        return HttpResponseBadRequest("No tiene permiso.")

    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    act.delete()
    _recalcular_avance_meta(meta)

    metas = MetaTactico.objects.filter(objetivo=objetivo).prefetch_related(
        "actividades", "actividades__ejecutores"
    ).order_by("-fecha_fin", "-id")
    return _render_oob_response(request, objetivo, metas, "Actividad eliminada")


@login_required
def actividad_estado_view(request, pk: int):
    """Toggle rápido: Completada <-> Pendiente (solo asignados o admin/rrhh)"""
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    act = get_object_or_404(Actividad, pk=pk)

    # Admin/RRHH (según tu sistema actual)
    es_admin_rrhh = request.user.is_superuser or getattr(request.user, "puede_ver_modulo_usuarios", False)

    # Empleado asociado al usuario
    empleado = getattr(request.user, "empleado", None)

    # Si NO es admin, debe estar asignado
    if not es_admin_rrhh:
        if empleado is None:
            return HttpResponseForbidden("No tienes un empleado asociado.")
        if not act.ejecutores.filter(pk=empleado.pk).exists():
            return HttpResponseForbidden("No estás asignado a esta actividad.")
        if not act.ejecutores.exists():
            return HttpResponseForbidden("La actividad no tiene ejecutores asignados.")

    # Toggle
    if act.estado == "completada":
        act.estado = "pendiente"
        act.porcentaje_avance = 0
    else:
        act.estado = "completada"
        act.porcentaje_avance = 100

    act.save(update_fields=["estado", "porcentaje_avance"])

    # Recalcular meta padre
    _recalcular_avance_meta(act.meta)

    # Refrescar UI
    metas = MetaTactico.objects.filter(objetivo=act.meta.objetivo).prefetch_related(
        "actividades", "actividades__ejecutores"
    ).order_by("-fecha_fin", "-id")

    return _render_oob_response(request, act.meta.objetivo, metas, "Estado actualizado")
