from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST 

from .models import SolicitudAusencia, AprobacionAusencia, TipoAusencia 
from .forms import AprobacionForm # Asegúrate de tener este form o usar HTML directo

# ---------------------------------------------------------
# 1. VISTA MAESTRA (Control de Tráfico)
# ---------------------------------------------------------
@login_required
def lista_solicitudes_view(request):
    """
    Vista principal del menú 'Solicitudes'.
    - Si es Admin/RRHH -> Ve todo.
    - Si es Empleado -> Se va a su vista personal.
    """
    usuario = request.user
    
    # Define aquí quién es "Jefe" según tus modelos
    es_jefe = (
        usuario.is_superuser or 
        getattr(usuario, 'es_admin_rrhh', False) or 
        getattr(usuario, 'es_superadmin_negocio', False)
    )

    if not es_jefe:
        return redirect('solicitudes:vista_empleado')

    # Lógica de Admin
    solicitudes = SolicitudAusencia.objects.all().order_by('-fecha_creacion')
    query = request.GET.get('q')
    
    if query:
        solicitudes = solicitudes.filter(
            Q(empleado__nombres__icontains=query) | 
            Q(empleado__apellidos__icontains=query) |
            Q(ausencia__nombre__icontains=query) |
            Q(motivo__icontains=query)
        ).distinct()
        
    return render(request, 'solicitudes/lista_solicitudes.html', {'solicitudes': solicitudes, 'query': query})


# ---------------------------------------------------------
# 2. VISTA EMPLEADO (Mis Solicitudes)
# ---------------------------------------------------------
@login_required
def empleado_view(request):
    if not hasattr(request.user, 'empleado'):
        return render(request, 'solicitudes/solicitudes_empleado.html', {'solicitudes': []})

    empleado_actual = request.user.empleado
    solicitudes = SolicitudAusencia.objects.filter(empleado=empleado_actual).order_by('-fecha_creacion')

    query = request.GET.get('q')
    if query:
        solicitudes = solicitudes.filter(
            Q(ausencia__nombre__icontains=query) |
            Q(motivo__icontains=query)
        )

    return render(request, 'solicitudes/solicitudes_empleado.html', {
        'solicitudes': solicitudes,
        'query': query
    })


# ---------------------------------------------------------
# 3. GESTIONAR SOLICITUD (Admin: Aprobar/Rechazar/Devolver)
# ---------------------------------------------------------
@login_required
def responer_solicitudes_view(request, solicitud_id):
    # Seguridad: Solo Jefes
    es_jefe = (
        request.user.is_superuser or 
        getattr(request.user, 'es_admin_rrhh', False) or 
        getattr(request.user, 'es_superadmin_negocio', False)
    )
    if not es_jefe:
        messages.error(request, "Acceso denegado.")
        return redirect('solicitudes:vista_empleado')

    solicitud = get_object_or_404(SolicitudAusencia, pk=solicitud_id)
    
    try:
        aprobador = request.user.empleado 
    except AttributeError:
        messages.error(request, "Tu usuario Admin no tiene ficha de empleado.")
        return redirect('solicitudes:lista_solicitudes')
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        comentario = request.POST.get('comentario')
        
        if accion in ['aprobar', 'rechazar', 'devolver']:
            # 1. Historial
            AprobacionAusencia.objects.create(
                solicitud=solicitud,
                aprobador=aprobador,
                accion=accion,
                comentario=comentario
            )

            # 2. Cambio de Estado
            if accion == 'aprobar':
                solicitud.estado = SolicitudAusencia.Estado.APROBADO
            elif accion == 'rechazar':
                solicitud.estado = SolicitudAusencia.Estado.RECHAZADO
            elif accion == 'devolver':
                solicitud.estado = SolicitudAusencia.Estado.DEVUELTO
            
            solicitud.save()
            
            if accion == 'devolver':
                messages.warning(request, "Solicitud devuelta para corrección.")
            else:
                messages.success(request, f"Solicitud {accion} exitosamente.")
                
            return redirect('solicitudes:lista_solicitudes')

    return render(request, 'solicitudes/responder_solicitudes.html', {
        'solicitud': solicitud,
        'aprobaciones_previas': solicitud.aprobaciones.all().order_by('-fecha_accion')
    })


# ---------------------------------------------------------
# 4. CREAR SOLICITUD
# ---------------------------------------------------------
@login_required
def crear_solicitud_view(request):
    if not hasattr(request.user, 'empleado'):
        messages.error(request, "No eres empleado.")
        return redirect('solicitudes:lista_solicitudes')

    empleado = request.user.empleado

    if request.method == 'POST':
        try:
            # Captura básica manual (o usa forms.py si prefieres)
            ausencia_id = request.POST.get('ausencia')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            dias_habiles = request.POST.get('dias_habiles')
            motivo = request.POST.get('motivo')
            
            if all([ausencia_id, fecha_inicio, fecha_fin, dias_habiles, motivo]):
                nueva = SolicitudAusencia(
                    empresa=empleado.empresa,
                    empleado=empleado,
                    ausencia_id=ausencia_id, 
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    dias_habiles=dias_habiles,
                    motivo=motivo,
                    estado=SolicitudAusencia.Estado.PENDIENTE
                )
                if 'adjunto' in request.FILES:
                    nueva.adjunto_url = request.FILES['adjunto'].name 
                nueva.save()
                messages.success(request, "Solicitud creada.")
                return redirect('solicitudes:vista_empleado')
        except Exception as e:
            messages.error(request, f"Error: {e}")

    tipos = TipoAusencia.objects.filter(empresa=empleado.empresa, estado=True)
    return render(request, 'solicitudes/crear_solicitud.html', {'tipos_ausencia': tipos})


# ---------------------------------------------------------
# 5. EDITAR (Permite Pendiente y Devuelto)
# ---------------------------------------------------------
@login_required
def editar_solicitud_view(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudAusencia, pk=solicitud_id)
    
    # Solo dueño
    if solicitud.empleado != request.user.empleado:
        return redirect('solicitudes:vista_empleado')
    
    # Solo editable si Pendiente o Devuelto
    if solicitud.estado not in [SolicitudAusencia.Estado.PENDIENTE, SolicitudAusencia.Estado.DEVUELTO]:
        messages.warning(request, "No puedes editar esta solicitud.")
        return redirect('solicitudes:vista_empleado')

    if request.method == 'POST':
        solicitud.ausencia_id = request.POST.get('ausencia')
        solicitud.fecha_inicio = request.POST.get('fecha_inicio')
        solicitud.fecha_fin = request.POST.get('fecha_fin')
        solicitud.dias_habiles = request.POST.get('dias_habiles')
        solicitud.motivo = request.POST.get('motivo')
        
        if 'adjunto' in request.FILES:
            solicitud.adjunto_url = request.FILES['adjunto'].name 
        
        # Al editar, vuelve a PENDIENTE para que RRHH la vea de nuevo
        solicitud.estado = SolicitudAusencia.Estado.PENDIENTE
        solicitud.save()
        
        messages.success(request, "Solicitud corregida y enviada.")
        return redirect('solicitudes:vista_empleado')

    tipos = TipoAusencia.objects.filter(empresa=request.user.empleado.empresa, estado=True)
    return render(request, 'solicitudes/crear_solicitud.html', {
        'tipos_ausencia': tipos, 'solicitud': solicitud, 'es_edicion': True
    })


# ---------------------------------------------------------
# 6. ELIMINAR
# ---------------------------------------------------------
@login_required
@require_POST
def eliminar_solicitud_view(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudAusencia, pk=solicitud_id)
    
    # Solo dueño y si está pendiente/devuelto
    if solicitud.empleado == request.user.empleado and solicitud.estado in [SolicitudAusencia.Estado.PENDIENTE, SolicitudAusencia.Estado.DEVUELTO]:
        solicitud.delete()
        messages.success(request, "Eliminada.")
    else:
        messages.error(request, "No se puede eliminar.")
        
    return redirect('solicitudes:vista_empleado')