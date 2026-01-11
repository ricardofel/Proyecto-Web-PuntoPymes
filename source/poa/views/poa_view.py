from datetime import date
from decimal import Decimal
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponseBadRequest, HttpResponse
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

def _recalcular_avance_meta(meta):
    """
    Recalcula el valor_actual de una meta basado en el % de actividades completadas.
    Priorizamos el cálculo automático sobre la edición manual.
    """
    total_actividades = meta.actividades.count()
    
    if total_actividades == 0:
        meta.valor_actual = Decimal('0.00')
    else:
        completadas = meta.actividades.filter(estado='completada').count()
        ratio = Decimal(completadas) / Decimal(total_actividades)
        meta.valor_actual = meta.valor_esperado * ratio
    
    meta.save(update_fields=['valor_actual'])

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

    # Optimización: prefetch de metas para evitar N+1 si accedemos a ellas
    objetivos_qs = qs.prefetch_related('metas_tacticas').order_by("-fecha_creacion")
    
    # Conteos optimizados
    metas_count = MetaTactico.objects.filter(objetivo__in=objetivos_qs).count()
    actividades_count = Actividad.objects.filter(meta__objetivo__in=objetivos_qs).count()
    
    objetivos_list = list(objetivos_qs)
    
    # --- CORRECCIÓN AQUÍ (estaba como 'objectives_list') ---
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
    Versión robusta usando HX-Trigger Headers.
    """
    response_content = ""
    
    # 1. Actualizar contenedor de metas si se provee
    if metas_qs is not None:
        lista_html = render_to_string("poa/partials/meta_list.html", {"metas": metas_qs}, request)
        response_content += f'<div hx-swap-oob="innerHTML:#metas-container">{lista_html}</div>'

    # 2. Actualizar header del objetivo si se provee
    if objetivo is not None:
        header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": objetivo}, request)
        response_content += f'<div hx-swap-oob="innerHTML:#objetivo-header">{header_html}</div>'

    # 3. CREAR LA RESPUESTA Y ADJUNTAR LA SEÑAL EN EL HEADER
    response = HttpResponse(response_content)
    
    # Esto dispara el evento 'close-modal' en el navegador con el mensaje
    trigger_data = {"close-modal": toast_msg}
    response["HX-Trigger"] = json.dumps(trigger_data)

    return response

# --- VISTAS PRINCIPALES ---

@login_required
def poa_view(request):
    anio = _anio_actual_from_request(request)
    anios = list(range(anio - 2, anio + 2)) # Muestra año siguiente también
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
    # 1. Validar método
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    # 2. Definir variables (ESTAS ERAN LAS QUE FALTABAN)
    anio = _anio_actual_from_request(request)
    form = ObjetivoForm(request.POST)

    # 3. Validar formulario
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

            # 4. Actualizar dashboard via OOB
            context_dash = _build_dashboard_context(request, anio)
            dashboard_html = render_to_string("poa/partials/dashboard_cards.html", context_dash, request)
            
            # --- SOLUCIÓN DE MODAL (HEADERS) ---
            # Preparamos la respuesta con el HTML nuevo
            response = HttpResponse(f'<div hx-swap-oob="innerHTML:#poa-dashboard">{dashboard_html}</div>')
            
            # Enviamos la orden de cierre en la cabecera para que el script del frontend la capture
            trigger_data = {"close-modal": "Objetivo creado"}
            response["HX-Trigger"] = json.dumps(trigger_data)
            
            return response

    # 5. Si hay errores, devolvemos el formulario
    return render(request, "poa/partials/modal_objetivo.html", {"form": form, "anio_actual": anio})

    return render(request, "poa/partials/modal_objetivo.html", {"form": form, "anio_actual": anio})
@login_required
def objetivo_detalle_view(request, pk: int):
    objetivo = get_object_or_404(Objetivo, pk=pk)
    if not _verificar_permiso_empresa(request, objetivo):
        return HttpResponseBadRequest("Objetivo no pertenece a la empresa actual.")
    
    # Optimización con prefetch_related para actividades y ejecutores
    metas = MetaTactico.objects.filter(objetivo=objetivo).prefetch_related(
        'actividades', 
        'actividades__ejecutores'
    ).order_by("-fecha_fin", "-id")

    return render(request, "poa/objetivo_detalle.html", {
        "objetivo": objetivo, 
        "metas": metas, 
        "meta_form": MetaTacticoForm()
    })


@login_required
def objetivo_metas_partial(request, pk: int):
    """Carga solo la lista de metas (útil para refrescos o carga lazy)."""
    objetivo = get_object_or_404(Objetivo, pk=pk)
    if not _verificar_permiso_empresa(request, objetivo):
        return HttpResponseBadRequest("Objetivo no pertenece a la empresa actual.")
        
    metas = MetaTactico.objects.filter(objetivo=objetivo).prefetch_related(
        'actividades', 
        'actividades__ejecutores'
    ).order_by("-fecha_fin", "-id")
    
    return render(request, "poa/partials/meta_list.html", {"objetivo": objetivo, "metas": metas})


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
            
            # --- LÓGICA ACTUALIZADA (HEADERS) ---
            referer = request.META.get('HTTP_REFERER', '')
            response_content = ""
            
            if "objetivos/" in referer and "dashboard" not in referer:
                # Caso A: Detalle -> Actualizar Header
                header_html = render_to_string("poa/partials/objetivo_header.html", {"objetivo": obj}, request)
                response_content = f'<div hx-swap-oob="innerHTML:#objetivo-header">{header_html}</div>'
            else:
                # Caso B: Dashboard -> Actualizar Card
                anio = obj.anio
                context_dash = _build_dashboard_context(request, anio)
                dashboard_html = render_to_string("poa/partials/dashboard_cards.html", context_dash, request)
                response_content = f'<div hx-swap-oob="innerHTML:#poa-dashboard">{dashboard_html}</div>'

            response = HttpResponse(response_content)
            # Enviamos la señal de cierre al frontend
            trigger_data = {"close-modal": "Objetivo actualizado"}
            response["HX-Trigger"] = json.dumps(trigger_data)
            
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

    if request.method == "POST":
        obj.delete()
        
        # Si estaba en detalle, redirigir
        referer = request.META.get('HTTP_REFERER', '')
        if "objetivos/" in referer and "dashboard" not in referer:
             return HttpResponse(status=200, headers={"HX-Redirect": reverse('poa:poa')})
        
        # Si estaba en dashboard, actualizar in-situ
        anio = _anio_actual_from_request(request)
        context_dash = _build_dashboard_context(request, anio)
        dashboard_html = render_to_string("poa/partials/dashboard_cards.html", context_dash, request)
        
        return HttpResponse(f"""
            <div hx-swap-oob="innerHTML:#poa-dashboard">{dashboard_html}</div>
            <script>Swal.fire({{icon: 'success', title: 'Objetivo eliminado', toast: true, position: 'top-end', showConfirmButton: false, timer: 3000}});</script>
        """)

    return HttpResponseBadRequest()


@login_required
@solo_superusuario_o_admin_rrhh
def cambiar_estado_objetivo(request, pk):
    objetivo = get_object_or_404(Objetivo, pk=pk)
    if not _verificar_permiso_empresa(request, objetivo):
        return HttpResponseBadRequest("Sin permiso")
    
    if objetivo.estado == 'activo':
        objetivo.estado = 'cerrado'
        messages.warning(request, f"El objetivo '{objetivo.nombre}' ha sido cerrado.")
    else:
        objetivo.estado = 'activo'
        messages.success(request, f"El objetivo '{objetivo.nombre}' ahora está activo.")
    
    objetivo.save()
    return redirect('poa:objetivo_detalle', pk=pk)


# --- GESTIÓN DE METAS ---

@login_required
@solo_superusuario_o_admin_rrhh
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
            
            # Refrescar lista optimizada
            metas = MetaTactico.objects.filter(objetivo=objetivo).prefetch_related('actividades', 'actividades__ejecutores').order_by("-fecha_fin", "-id")
            return _render_oob_response(request, objetivo, metas, "Meta creada")
            
        # Si hay errores en el POST, devolvemos el form con errores
        return render(request, "poa/partials/modal_meta.html", {"objetivo": objetivo, "meta_form": form})
    
    # --- AGREGAR ESTO PARA MANEJAR EL GET ---
    else:
        form = MetaTacticoForm()
    
    return render(request, "poa/partials/modal_meta.html", {
        "objetivo": objetivo, 
        "meta_form": form
    })


@login_required
@solo_superusuario_o_admin_rrhh
def meta_editar_view(request, pk: int):
    meta = get_object_or_404(MetaTactico, pk=pk)
    
    # Verificación de permisos (ahora con bypass para superusuario)
    if not _verificar_permiso_empresa(request, meta.objetivo):
        return HttpResponseBadRequest("Sin permiso")

    if request.method == "POST":
        form = MetaTacticoForm(request.POST, instance=meta)
        if form.is_valid():
            form.save()
            
            # Recargar la lista de metas ordenada
            metas = MetaTactico.objects.filter(objetivo=meta.objetivo).prefetch_related('actividades', 'actividades__ejecutores').order_by("-fecha_fin", "-id")
            
            # Usar el helper robusto (que envía el HX-Trigger)
            return _render_oob_response(request, meta.objetivo, metas, "Meta actualizada")
    else:
        form = MetaTacticoForm(instance=meta)

    return render(request, "poa/partials/modal_meta.html", {
        "objetivo": meta.objetivo, 
        "meta_form": form, 
        "is_edit": True, 
        "edit_url": request.path
    })


@login_required
@solo_superusuario_o_admin_rrhh
def meta_eliminar_view(request, pk: int):
    meta = get_object_or_404(MetaTactico, pk=pk)
    objetivo = meta.objetivo
    if not _verificar_permiso_empresa(request, objetivo):
        return HttpResponseBadRequest("No tiene permiso.")

    if request.method == "POST":
        meta.delete()
        metas = MetaTactico.objects.filter(objetivo=objetivo).prefetch_related('actividades', 'actividades__ejecutores').order_by("-fecha_fin", "-id")
        return _render_oob_response(request, objetivo, metas, "Meta eliminada")
        
    return HttpResponseBadRequest()


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
            form.save_m2m() # [FIX] Guardar ejecutores
            
            _recalcular_avance_meta(meta)

            metas = MetaTactico.objects.filter(objetivo=meta.objetivo).prefetch_related('actividades', 'actividades__ejecutores').order_by("-fecha_fin", "-id")
            return _render_oob_response(request, meta.objetivo, metas, "Actividad creada")
        
        return render(request, "poa/partials/modal_actividad.html", {"form": form, "meta_id": pk, "meta_nombre": meta.nombre})

    return render(request, "poa/partials/modal_actividad.html", {
        "form": ActividadForm(), 
        "meta_id": pk, 
        "meta_nombre": meta.nombre
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
            
            metas = MetaTactico.objects.filter(objetivo=act.meta.objetivo).prefetch_related('actividades', 'actividades__ejecutores').order_by("-fecha_fin", "-id")
            return _render_oob_response(request, act.meta.objetivo, metas, "Actividad actualizada")
    else:
        form = ActividadForm(instance=act)

    return render(request, "poa/partials/modal_actividad.html", {
        "form": form, 
        "meta_id": act.meta.id, 
        "meta_nombre": act.meta.nombre, 
        "is_edit": True, 
        "edit_url": request.path
    })


@login_required
@solo_superusuario_o_admin_rrhh
def actividad_eliminar_view(request, pk: int):
    act = get_object_or_404(Actividad, pk=pk)
    meta = act.meta
    objetivo = meta.objetivo
    
    if not _verificar_permiso_empresa(request, objetivo):
        return HttpResponseBadRequest("No tiene permiso.")

    if request.method == "POST":
        act.delete()
        _recalcular_avance_meta(meta)
        
        metas = MetaTactico.objects.filter(objetivo=objetivo).prefetch_related('actividades', 'actividades__ejecutores').order_by("-fecha_fin", "-id")
        return _render_oob_response(request, objetivo, metas, "Actividad eliminada")
        
    return HttpResponseBadRequest()


@login_required
def actividad_estado_view(request, pk: int):
    """ Toggle rápido: Completada <-> Pendiente """
    act = get_object_or_404(Actividad, pk=pk)
    
    # Toggle simple de estado
    if act.estado == 'completada':
        act.estado = 'pendiente'
        act.porcentaje_avance = 0
    else:
        act.estado = 'completada'
        act.porcentaje_avance = 100
    
    act.save(update_fields=['estado', 'porcentaje_avance'])
    
    # Recalcular meta padre
    _recalcular_avance_meta(act.meta)

    # Refrescar UI
    metas = MetaTactico.objects.filter(objetivo=act.meta.objetivo).prefetch_related('actividades', 'actividades__ejecutores').order_by("-fecha_fin", "-id")
    return _render_oob_response(request, act.meta.objetivo, metas, "Estado actualizado")