from datetime import date
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from usuarios.decorators import solo_superusuario_o_admin_rrhh
from poa.forms import ObjetivoForm, MetaTacticoForm, ActividadForm
from poa.models import Objetivo, MetaTactico, Actividad
from decimal import Decimal

def _anio_actual_from_request(request) -> int:
    raw = request.GET.get("anio") or request.POST.get("anio")
    if raw:
        try:
            return int(raw)
        except ValueError:
            return date.today().year
    return date.today().year


def _empresa_actual(request):
    empresa = getattr(request, "empresa_actual", None)
    if empresa is not None:
        return empresa
    empresa = getattr(request.user, "empresa", None)
    if empresa is not None:
        return empresa
    empleado = getattr(request.user, "empleado", None)
    if empleado is not None:
        return getattr(empleado, "empresa", None)
    return None


def _build_dashboard_context(request, anio: int):
    q = (request.GET.get("q") or "").strip()
    estado = (request.GET.get("estado") or "").strip()

    qs = Objetivo.objects.filter(anio=anio)
    empresa = _empresa_actual(request)
    if empresa is not None:
        qs = qs.filter(empresa=empresa)

    if q:
        qs = qs.filter(nombre__icontains=q)
    if estado:
        qs = qs.filter(estado=estado)

    objetivos_qs = qs.order_by("-fecha_creacion")
    
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


def poa_view(request):
    anio = _anio_actual_from_request(request)
    anios = list(range(anio - 2, anio + 1))
    context = {"anio_actual": anio, "anios": anios, "form": ObjetivoForm()}
    context.update(_build_dashboard_context(request, anio))
    return render(request, "poa/poa.html", context)


def poa_dashboard_partial(request):
    anio = _anio_actual_from_request(request)
    context = _build_dashboard_context(request, anio)
    return render(request, "poa/partials/dashboard_cards.html", context)


def objetivo_crear_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    anio = _anio_actual_from_request(request)
    form = ObjetivoForm(request.POST)

    if form.is_valid():
        objetivo = form.save(commit=False)
        objetivo.anio = anio
        empresa = _empresa_actual(request)
        if empresa is None:
            form.add_error(None, "No tienes una empresa asignada.")
        else:
            objetivo.empresa = empresa
            objetivo.save()
            context_dash = _build_dashboard_context(request, anio)
            dashboard_html = render_to_string("poa/partials/dashboard_cards.html", context_dash, request)
            return render(request, "poa/partials/modal_objetivo.html", {
                "form": ObjetivoForm(), "anio_actual": anio, "success": True, "dashboard_html": dashboard_html
            })

    return render(request, "poa/partials/modal_objetivo.html", {"form": form, "anio_actual": anio})


def objetivo_detalle_view(request, pk: int):
    empresa = _empresa_actual(request)
    objetivo = get_object_or_404(Objetivo, pk=pk)
    if empresa is not None and objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("Objetivo no pertenece a la empresa actual.")
    metas = MetaTactico.objects.filter(objetivo=objetivo).order_by("-fecha_fin", "-id")
    return render(request, "poa/objetivo_detalle.html", {
        "objetivo": objetivo, "metas": metas, "meta_form": MetaTacticoForm()
    })


def objetivo_metas_partial(request, pk: int):
    empresa = _empresa_actual(request)
    objetivo = get_object_or_404(Objetivo, pk=pk)
    if empresa is not None and objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("Objetivo no pertenece a la empresa actual.")
    metas = MetaTactico.objects.filter(objetivo=objetivo).order_by("-fecha_fin", "-id")
    return render(request, "poa/partials/meta_list.html", {"objetivo": objetivo, "metas": metas})


def meta_crear_view(request, pk: int):
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")
    objetivo = get_object_or_404(Objetivo, pk=pk)
    empresa = _empresa_actual(request)
    if empresa is not None and objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("No tiene permiso.")

    form = MetaTacticoForm(request.POST)
    if form.is_valid():
        meta = form.save(commit=False)
        meta.objetivo = objetivo
        meta.save()
        metas = MetaTactico.objects.filter(objetivo=objetivo).order_by("-fecha_fin", "-id")
        lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
        header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": objetivo}, request)
        return render(request, "poa/partials/modal_meta.html", {
            "objetivo": objetivo, "meta_form": MetaTacticoForm(), "success": True, 
            "lista_html": lista_html, "header_html": header_html
        })
    return render(request, "poa/partials/modal_meta.html", {"objetivo": objetivo, "meta_form": form})


# ==========================================
#  GESTIÓN DE METAS (Editar / Eliminar)
# ==========================================

@login_required
@solo_superusuario_o_admin_rrhh
def meta_editar_view(request, pk: int):
    meta = get_object_or_404(MetaTactico, pk=pk)
    empresa = _empresa_actual(request)
    if empresa and meta.objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("Sin permiso")

    if request.method == "POST":
        form = MetaTacticoForm(request.POST, instance=meta)
        if form.is_valid():
            form.save()
            metas = MetaTactico.objects.filter(objetivo=meta.objetivo).order_by("-fecha_fin", "-id")
            lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
            header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": meta.objetivo}, request)
            return render(request, "poa/partials/modal_meta.html", {
                "objetivo": meta.objetivo, "meta_form": MetaTacticoForm(), "success": True, 
                "lista_html": lista_html, "header_html": header_html, "is_edit": True
            })
    else:
        form = MetaTacticoForm(instance=meta)

    response = render(request, "poa/partials/modal_meta.html", {
        "objetivo": meta.objetivo, "meta_form": form, "is_edit": True, "edit_url": request.path
    })
    response.content += b"<script>new bootstrap.Modal(document.getElementById('modalMetaCrear')).show();</script>"
    return response


@login_required
@solo_superusuario_o_admin_rrhh
def meta_eliminar_view(request, pk: int):
    meta = get_object_or_404(MetaTactico, pk=pk)
    objetivo = meta.objetivo
    empresa = _empresa_actual(request)
    if empresa and objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("No tiene permiso.")

    if request.method == "POST":
        meta.delete()
        metas = MetaTactico.objects.filter(objetivo=objetivo).order_by("-fecha_fin", "-id")
        lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
        header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": objetivo}, request)
        
        return HttpResponse(f"""
            <div hx-swap-oob="innerHTML:#metas-container">{lista_html}</div>
            <div hx-swap-oob="innerHTML:#objetivo-header">{header_html}</div>
            <script>Swal.fire({{icon: 'success', title: 'Meta eliminada', toast: true, position: 'top-end', showConfirmButton: false, timer: 3000}});</script>
        """)
    return HttpResponseBadRequest()

def _recalcular_avance_meta(meta):
    """
    Función auxiliar para recalcular el valor_actual de una meta
    basado en el porcentaje de actividades completadas.
    """
    total_actividades = meta.actividades.count()
    
    if total_actividades == 0:
        meta.valor_actual = 0
    else:
        completadas = meta.actividades.filter(estado='completada').count()
        # Calculamos el porcentaje (0.0 a 1.0)
        ratio = Decimal(completadas) / Decimal(total_actividades)
        # Aplicamos ese porcentaje al valor esperado de la meta
        meta.valor_actual = meta.valor_esperado * ratio
    
    meta.save()

# ==========================================
#  GESTIÓN DE ACTIVIDADES
# ==========================================

def actividad_crear_view(request, pk: int):
    meta = get_object_or_404(MetaTactico, pk=pk)
    empresa = _empresa_actual(request)
    if empresa is not None and meta.objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("No tiene permiso.")

    if request.method == "POST":
        form = ActividadForm(request.POST)
        if form.is_valid():
            actividad = form.save(commit=False)
            actividad.meta = meta
            actividad.save()
            
            # 1. Recalcular avance
            _recalcular_avance_meta(meta)

            # 2. Refrescar listas
            metas = MetaTactico.objects.filter(objetivo=meta.objetivo).order_by("-fecha_fin", "-id")
            lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
            header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": meta.objetivo}, request) # Para actualizar el % del objetivo también

            # Usamos OOB para actualizar el header del objetivo también
            return HttpResponse(f"""
                <div hx-swap-oob="innerHTML:#metas-container">{lista_html}</div>
                <div hx-swap-oob="innerHTML:#objetivo-header">{header_html}</div>
                <script>
                    var el = document.getElementById('modalActividadCrear');
                    var m = bootstrap.Modal.getInstance(el);
                    if (m) m.hide();
                    Swal.fire({{
                        icon: 'success', title: 'Actividad creada', toast: true, 
                        position: 'top-end', showConfirmButton: false, timer: 3000
                    }});
                </script>
            """)
        
        return render(request, "poa/partials/modal_actividad.html", {"form": form, "meta_id": pk, "meta_nombre": meta.nombre})

    response = render(request, "poa/partials/modal_actividad.html", {"form": ActividadForm(), "meta_id": pk, "meta_nombre": meta.nombre})
    response.content += b"<script>var el = document.getElementById('modalActividadCrear'); var m = new bootstrap.Modal(el); m.show();</script>"
    return response


@login_required
def actividad_estado_view(request, pk: int):
    """ Toggle rápido: Completada <-> Pendiente """
    act = get_object_or_404(Actividad, pk=pk)
    
    if act.estado == 'completada':
        act.estado = 'pendiente'
        act.porcentaje_avance = 0
    else:
        act.estado = 'completada'
        act.porcentaje_avance = 100
    act.save()

    # 1. Recalcular avance
    _recalcular_avance_meta(act.meta)

    # 2. Refrescar listas y header
    metas = MetaTactico.objects.filter(objetivo=act.meta.objetivo).order_by("-fecha_fin", "-id")
    lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
    header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": act.meta.objetivo}, request)
    
    return HttpResponse(f"""
        <div hx-swap-oob="innerHTML:#metas-container">{lista_html}</div>
        <div hx-swap-oob="innerHTML:#objetivo-header">{header_html}</div>
    """)


@login_required
@solo_superusuario_o_admin_rrhh
def actividad_editar_view(request, pk: int):
    act = get_object_or_404(Actividad, pk=pk)
    empresa = _empresa_actual(request)
    if empresa is not None and act.meta.objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("No tiene permiso.")

    if request.method == "POST":
        form = ActividadForm(request.POST, instance=act)
        if form.is_valid():
            form.save()
            
            # 1. Recalcular (por si cambió el estado manualmente en el form)
            _recalcular_avance_meta(act.meta)
            
            # 2. Refrescar
            metas = MetaTactico.objects.filter(objetivo=act.meta.objetivo).order_by("-fecha_fin", "-id")
            lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
            header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": act.meta.objetivo}, request)
            
            return HttpResponse(f"""
                <div hx-swap-oob="innerHTML:#metas-container">{lista_html}</div>
                <div hx-swap-oob="innerHTML:#objetivo-header">{header_html}</div>
                <script>
                    var el = document.getElementById('modalActividadCrear');
                    var m = bootstrap.Modal.getInstance(el);
                    if (m) m.hide();
                    Swal.fire({{icon: 'success', title: 'Actividad actualizada', toast: true, position: 'top-end', showConfirmButton: false, timer: 3000}});
                </script>
            """)
    else:
        form = ActividadForm(instance=act)

    response = render(request, "poa/partials/modal_actividad.html", {
        "form": form, "meta_id": act.meta.id, "meta_nombre": act.meta.nombre, 
        "is_edit": True, "edit_url": request.path
    })
    response.content += b"<script>new bootstrap.Modal(document.getElementById('modalActividadCrear')).show();</script>"
    return response


@login_required
@solo_superusuario_o_admin_rrhh
def actividad_eliminar_view(request, pk: int):
    act = get_object_or_404(Actividad, pk=pk)
    meta = act.meta
    objetivo = meta.objetivo
    
    empresa = _empresa_actual(request)
    if empresa is not None and objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("No tiene permiso.")

    if request.method == "POST":
        act.delete()
        
        # 1. Recalcular (importante: al borrar, el total baja y el porcentaje cambia)
        _recalcular_avance_meta(meta)
        
        # 2. Refrescar
        metas = MetaTactico.objects.filter(objetivo=objetivo).order_by("-fecha_fin", "-id")
        lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
        header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": objetivo}, request)
        
        return HttpResponse(f"""
            <div hx-swap-oob="innerHTML:#metas-container">{lista_html}</div>
            <div hx-swap-oob="innerHTML:#objetivo-header">{header_html}</div>
            <script>Swal.fire({{icon: 'success', title: 'Actividad eliminada', toast: true, position: 'top-end', showConfirmButton: false, timer: 3000}});</script>
        """)
        
    return HttpResponseBadRequest()


@login_required
@solo_superusuario_o_admin_rrhh
def objetivo_editar_view(request, pk: int):
    obj = get_object_or_404(Objetivo, pk=pk)
    
    # Seguridad de Empresa
    empresa = _empresa_actual(request)
    if empresa and obj.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("Sin permiso")

    if request.method == "POST":
        form = ObjetivoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            
            # Detectar desde dónde se editó para saber qué actualizar
            # Si estamos en la vista de detalle, actualizamos el header
            if "objetivos/" in request.META.get('HTTP_REFERER', ''):
                header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": obj}, request)
                return HttpResponse(f"""
                    <div hx-swap-oob="innerHTML:#objetivo-header">{header_html}</div>
                    <script>
                        var el = document.getElementById('modalObjetivoCrear');
                        var m = bootstrap.Modal.getInstance(el);
                        if (m) m.hide();
                        Swal.fire({{icon: 'success', title: 'Objetivo actualizado', toast: true, position: 'top-end', showConfirmButton: false, timer: 3000}});
                    </script>
                """)
            else:
                # Si estamos en el dashboard, actualizamos todo el dashboard
                anio = obj.anio
                context_dash = _build_dashboard_context(request, anio)
                dashboard_html = render_to_string("poa/partials/dashboard_cards.html", context_dash, request)
                return HttpResponse(f"""
                    <div hx-swap-oob="innerHTML:#poa-dashboard">{dashboard_html}</div>
                    <script>
                        var el = document.getElementById('modalObjetivoCrear');
                        var m = bootstrap.Modal.getInstance(el);
                        if (m) m.hide();
                        Swal.fire({{icon: 'success', title: 'Objetivo actualizado', toast: true, position: 'top-end', showConfirmButton: false, timer: 3000}});
                    </script>
                """)
    else:
        form = ObjetivoForm(instance=obj)

    # Reutilizamos el modal de crear, pero en modo edición
    response = render(request, "poa/partials/modal_objetivo.html", {
        "form": form,
        "anio_actual": obj.anio,
        "is_edit": True,
        "edit_url": request.path
    })
    response.content += b"<script>new bootstrap.Modal(document.getElementById('modalObjetivoCrear')).show();</script>"
    return response


@login_required
@solo_superusuario_o_admin_rrhh
def objetivo_eliminar_view(request, pk: int):
    obj = get_object_or_404(Objetivo, pk=pk)
    empresa = _empresa_actual(request)
    if empresa and obj.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("Sin permiso")

    if request.method == "POST":
        obj.delete()
        
        # Si la petición viene del detalle del objetivo, debemos redirigir al tablero
        if "objetivos/" in request.META.get('HTTP_REFERER', ''):
             from django.shortcuts import redirect
             return HttpResponse(status=200, headers={"HX-Redirect": "/poa/"})
        
        # Si viene del dashboard, actualizamos el dashboard in-situ
        anio = _anio_actual_from_request(request)
        context_dash = _build_dashboard_context(request, anio)
        dashboard_html = render_to_string("poa/partials/dashboard_cards.html", context_dash, request)
        
        return HttpResponse(f"""
            <div hx-swap-oob="innerHTML:#poa-dashboard">{dashboard_html}</div>
            <script>Swal.fire({{icon: 'success', title: 'Objetivo eliminado', toast: true, position: 'top-end', showConfirmButton: false, timer: 3000}});</script>
        """)

    return HttpResponseBadRequest()