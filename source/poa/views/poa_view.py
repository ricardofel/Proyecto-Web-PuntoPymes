from datetime import date
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse # Para respuestas simples de HTMX
from usuarios.decorators import solo_superusuario_o_admin_rrhh # Tu decorador personalizado

# ✅ IMPORTACIONES CRÍTICAS (Aquí estaba el error)
from poa.forms import ObjetivoForm, MetaTacticoForm, ActividadForm
from poa.models import Objetivo, MetaTactico, Actividad


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

    # Aquí fallaba antes porque no encontraba 'Objetivo'
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
    actividades_count = Actividad.objects.filter(
        meta__objetivo__in=objetivos_qs
    ).count()

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

    context = {
        "anio_actual": anio,
        "anios": anios,
        "form": ObjetivoForm(),
    }
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
            form.add_error(
                None, "No tienes una empresa asignada. Contacta al administrador."
            )
        else:
            objetivo.empresa = empresa
            objetivo.save()

            # --- CASO ÉXITO ---
            context_dash = _build_dashboard_context(request, anio)
            dashboard_html = render_to_string(
                "poa/partials/dashboard_cards.html", context_dash, request
            )
            
            return render(
                request, 
                "poa/partials/modal_objetivo.html", 
                {
                    "form": ObjetivoForm(), 
                    "anio_actual": anio,
                    "success": True, 
                    "dashboard_html": dashboard_html
                }
            )

    return render(
        request, "poa/partials/modal_objetivo.html", {"form": form, "anio_actual": anio}
    )


def objetivo_detalle_view(request, pk: int):
    empresa = _empresa_actual(request)
    objetivo = get_object_or_404(Objetivo, pk=pk)

    if empresa is not None and objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("Objetivo no pertenece a la empresa actual.")

    metas = MetaTactico.objects.filter(objetivo=objetivo).order_by("-fecha_fin", "-id")

    context = {
        "objetivo": objetivo,
        "metas": metas,
        "meta_form": MetaTacticoForm(),
    }
    return render(request, "poa/objetivo_detalle.html", context)


def objetivo_metas_partial(request, pk: int):
    empresa = _empresa_actual(request)
    objetivo = get_object_or_404(Objetivo, pk=pk)

    if empresa is not None and objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("Objetivo no pertenece a la empresa actual.")

    metas = MetaTactico.objects.filter(objetivo=objetivo).order_by("-fecha_fin", "-id")
    return render(
        request,
        "poa/partials/meta_list.html",
        {"objetivo": objetivo, "metas": metas},
    )


def meta_crear_view(request, pk: int):
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    objetivo = get_object_or_404(Objetivo, pk=pk)
    
    empresa = _empresa_actual(request)
    if empresa is not None and objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest(
            "No tiene permiso para agregar metas a este objetivo."
        )

    form = MetaTacticoForm(request.POST)
    if form.is_valid():
        meta = form.save(commit=False)
        meta.objetivo = objetivo
        meta.save()

        # --- CASO ÉXITO ---
        metas = MetaTactico.objects.filter(objetivo=objetivo).order_by("-fecha_fin", "-id")
        lista_html = render_to_string(
            "poa/partials/meta_list.html", {"metas": metas}, request
        )

        header_html = render_to_string(
            "poa/partials/objetivo_header.html", {"objetivo": objetivo}, request
        )

        return render(
            request,
            "poa/partials/modal_meta.html",
            {
                "objetivo": objetivo, 
                "meta_form": MetaTacticoForm(),
                "success": True,
                "lista_html": lista_html,
                "header_html": header_html
            }
        )

    return render(
        request,
        "poa/partials/modal_meta.html",
        {"objetivo": objetivo, "meta_form": form},
    )


def actividad_crear_view(request, pk: int):
    """
    Crea una actividad para la meta especificada (pk).
    """
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

            # --- CASO ÉXITO ---
            metas = MetaTactico.objects.filter(objetivo=meta.objetivo).order_by("-fecha_fin", "-id")
            lista_html = render_to_string(
                "poa/partials/meta_list.html", {"metas": metas}, request
            )

            return render(
                request,
                "poa/partials/modal_actividad.html",
                {
                    "form": ActividadForm(),
                    "meta_id": pk,
                    "meta_nombre": meta.nombre,
                    "success": True,
                    "lista_html": lista_html
                }
            )
        
        return render(
            request,
            "poa/partials/modal_actividad.html",
            {
                "form": form, 
                "meta_id": pk, 
                "meta_nombre": meta.nombre
            }
        )

    # GET: Mostrar modal
    response = render(
        request,
        "poa/partials/modal_actividad.html",
        {
            "form": ActividadForm(),
            "meta_id": pk,
            "meta_nombre": meta.nombre
        }
    )
    
    response.content += b"""
    <script>
        var el = document.getElementById('modalActividadCrear');
        var m = new bootstrap.Modal(el);
        m.show();
    </script>
    """
    
    return response

# ... imports y funciones anteriores ...

# ==========================================
#  GESTIÓN DE METAS (Editar / Eliminar)
# ==========================================

def meta_editar_view(request, pk: int):
    meta = get_object_or_404(MetaTactico, pk=pk)
    # Seguridad (Empresa)
    empresa = _empresa_actual(request)
    if empresa and meta.objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("Sin permiso")

    if request.method == "POST":
        form = MetaTacticoForm(request.POST, instance=meta)
        if form.is_valid():
            form.save()
            # Renderizamos la lista actualizada y el header (por si cambiaron valores)
            metas = MetaTactico.objects.filter(objetivo=meta.objetivo).order_by("-fecha_fin", "-id")
            lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
            header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": meta.objetivo}, request)
            
            # Usamos el mismo modal de "Crear" pero le pasamos success para que cierre
            return render(request, "poa/partials/modal_meta.html", {
                "objetivo": meta.objetivo, "meta_form": MetaTacticoForm(), # Form limpio para el futuro
                "success": True, "lista_html": lista_html, "header_html": header_html
            })
    else:
        form = MetaTacticoForm(instance=meta)

    # Reutilizamos el modal de creación pero con el formulario lleno
    response = render(request, "poa/partials/modal_meta.html", {
        "objetivo": meta.objetivo, "meta_form": form, "is_edit": True, "edit_url": request.path
    })
    # Truco: Abrir modal
    response.content += b"<script>new bootstrap.Modal(document.getElementById('modalMetaCrear')).show();</script>"
    return response


def meta_eliminar_view(request, pk: int):
    meta = get_object_or_404(MetaTactico, pk=pk)
    objetivo = meta.objetivo
    # Seguridad
    empresa = _empresa_actual(request)
    if empresa and objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("Sin permiso")

    if request.method == "POST":
        meta.delete()
        # Actualizar lista y header
        metas = MetaTactico.objects.filter(objetivo=objetivo).order_by("-fecha_fin", "-id")
        lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
        header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": objetivo}, request)
        
        return HttpResponse(f"""
            <div hx-swap-oob="innerHTML:#metas-container">{lista_html}</div>
            <div hx-swap-oob="innerHTML:#objetivo-header">{header_html}</div>
            <script>Swal.fire({{icon: 'success', title: 'Meta eliminada', toast: true, position: 'top-end', showConfirmButton: false, timer: 3000}});</script>
        """)
    return HttpResponseBadRequest()


# ==========================================
#  GESTIÓN DE ACTIVIDADES (Check / Edit / Del)
# ==========================================

def actividad_estado_view(request, pk: int):
    """ Toggle: Si está completada -> pendiente, y viceversa """
    act = get_object_or_404(Actividad, pk=pk)
    
    # Lógica simple de toggle
    if act.estado == 'completada':
        act.estado = 'pendiente'
        act.porcentaje_avance = 0
    else:
        act.estado = 'completada'
        act.porcentaje_avance = 100
    act.save()

    # Recalcular % de la Meta (Opcional, pero recomendado)
    # Por ahora solo refrescamos la lista visualmente
    metas = MetaTactico.objects.filter(objetivo=act.meta.objetivo).order_by("-fecha_fin", "-id")
    lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
    return HttpResponse(lista_html)


def actividad_editar_view(request, pk: int):
    act = get_object_or_404(Actividad, pk=pk)
    if request.method == "POST":
        form = ActividadForm(request.POST, instance=act)
        if form.is_valid():
            form.save()
            metas = MetaTactico.objects.filter(objetivo=act.meta.objetivo).order_by("-fecha_fin", "-id")
            lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
            
            return render(request, "poa/partials/modal_actividad.html", {
                "success": True, "lista_html": lista_html
            })
    else:
        form = ActividadForm(instance=act)

    response = render(request, "poa/partials/modal_actividad.html", {
        "form": form, "meta_id": act.meta.id, "meta_nombre": act.meta.nombre, 
        "is_edit": True, "edit_url": request.path
    })
    response.content += b"<script>new bootstrap.Modal(document.getElementById('modalActividadCrear')).show();</script>"
    return response


def actividad_eliminar_view(request, pk: int):
    act = get_object_or_404(Actividad, pk=pk)
    meta = act.meta
    if request.method == "POST":
        act.delete()
        metas = MetaTactico.objects.filter(objetivo=meta.objetivo).order_by("-fecha_fin", "-id")
        lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
        return HttpResponse(lista_html) # Devuelve la lista actualizada directamente
    return HttpResponseBadRequest()

    # ==========================================
#  GESTIÓN DE METAS (Editar / Eliminar)
# ==========================================

@login_required
@solo_superusuario_o_admin_rrhh
def meta_editar_view(request, pk: int):
    meta = get_object_or_404(MetaTactico, pk=pk)
    
    # Validación de empresa (Seguridad extra)
    empresa = _empresa_actual(request)
    if empresa and meta.objetivo.empresa_id != getattr(empresa, "id", None):
        return HttpResponseBadRequest("No tiene permiso sobre esta meta.")

    if request.method == "POST":
        form = MetaTacticoForm(request.POST, instance=meta)
        if form.is_valid():
            form.save()
            
            # Recargar listas para HTMX
            metas = MetaTactico.objects.filter(objetivo=meta.objetivo).order_by("-fecha_fin", "-id")
            lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
            header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": meta.objetivo}, request)
            
            # Reutilizamos el modal pero con success=True
            return render(request, "poa/partials/modal_meta.html", {
                "objetivo": meta.objetivo,
                "meta_form": MetaTacticoForm(),
                "success": True,
                "lista_html": lista_html,
                "header_html": header_html,
                "is_edit": True # Bandera para mensajes
            })
    else:
        form = MetaTacticoForm(instance=meta)

    # Renderizar modal en modo edición
    response = render(request, "poa/partials/modal_meta.html", {
        "objetivo": meta.objetivo,
        "meta_form": form,
        "is_edit": True,
        "edit_url": request.path # URL para que el form sepa a dónde enviar el POST
    })
    
    # Abrir modal automáticamente
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
        
        # Actualizar interfaz
        metas = MetaTactico.objects.filter(objetivo=objetivo).order_by("-fecha_fin", "-id")
        lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
        header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": objetivo}, request)
        
        # Respuesta OOB (Out of Band) para actualizar múltiples partes
        return HttpResponse(f"""
            <div hx-swap-oob="innerHTML:#metas-container">{lista_html}</div>
            <div hx-swap-oob="innerHTML:#objetivo-header">{header_html}</div>
            <script>
                Swal.fire({{
                    icon: 'success', 
                    title: 'Meta eliminada', 
                    toast: true, 
                    position: 'top-end', 
                    showConfirmButton: false, 
                    timer: 3000
                }});
            </script>
        """)
    return HttpResponseBadRequest()


# ==========================================
#  GESTIÓN DE ACTIVIDADES
# ==========================================

@login_required
def actividad_estado_view(request, pk: int):
    """ Toggle rápido: Completada <-> Pendiente """
    # Nota: Quizás aquí no quieras el decorador estricto para que los ejecutores puedan marcar su avance
    act = get_object_or_404(Actividad, pk=pk)
    
    if act.estado == 'completada':
        act.estado = 'pendiente'
        act.porcentaje_avance = 0
    else:
        act.estado = 'completada'
        act.porcentaje_avance = 100
    act.save()

    # Recargar la lista madre (Meta List)
    metas = MetaTactico.objects.filter(objetivo=act.meta.objetivo).order_by("-fecha_fin", "-id")
    lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
    
    return HttpResponse(lista_html)


@login_required
@solo_superusuario_o_admin_rrhh
def actividad_editar_view(request, pk: int):
    act = get_object_or_404(Actividad, pk=pk)
    
    if request.method == "POST":
        form = ActividadForm(request.POST, instance=act)
        if form.is_valid():
            form.save()
            metas = MetaTactico.objects.filter(objetivo=act.meta.objetivo).order_by("-fecha_fin", "-id")
            lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
            
            return render(request, "poa/partials/modal_actividad.html", {
                "success": True, 
                "lista_html": lista_html,
                "is_edit": True
            })
    else:
        form = ActividadForm(instance=act)

    response = render(request, "poa/partials/modal_actividad.html", {
        "form": form,
        "meta_id": act.meta.id,
        "meta_nombre": act.meta.nombre,
        "is_edit": True,
        "edit_url": request.path
    })
    response.content += b"<script>new bootstrap.Modal(document.getElementById('modalActividadCrear')).show();</script>"
    return response


@login_required
@solo_superusuario_o_admin_rrhh
def actividad_eliminar_view(request, pk: int):
    act = get_object_or_404(Actividad, pk=pk)
    meta = act.meta
    
    if request.method == "POST":
        act.delete()
        metas = MetaTactico.objects.filter(objetivo=meta.objetivo).order_by("-fecha_fin", "-id")
        lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas}, request)
        return HttpResponse(lista_html)
        
    return HttpResponseBadRequest()