from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST 
from django.http import FileResponse, Http404, JsonResponse

from .models import SolicitudAusencia, AprobacionAusencia, TipoAusencia, AdjuntoSolicitud
from .forms import AprobacionForm, SolicitudAusenciaForm
from core.storage import private_storage

# gestión de aprobación o rechazo por parte del jefe
@login_required
def responer_solicitudes_view(request, solicitud_id):
    es_jefe = (request.user.is_superuser or getattr(request.user, 'es_admin_rrhh', False) or getattr(request.user, 'es_superadmin_negocio', False))
    if not es_jefe:
        return redirect('solicitudes:vista_empleado')
    
    solicitud = get_object_or_404(SolicitudAusencia, pk=solicitud_id)
    try:
        aprobador = request.user.empleado 
    except AttributeError:
        return redirect('solicitudes:lista_solicitudes')
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        comentario = request.POST.get('comentario')
        
        if accion in ['aprobar', 'rechazar', 'devolver']:
            AprobacionAusencia.objects.create(solicitud=solicitud, aprobador=aprobador, accion=accion, comentario=comentario)
            
            if accion == 'aprobar': 
                solicitud.estado = SolicitudAusencia.Estado.APROBADO
            elif accion == 'rechazar': 
                solicitud.estado = SolicitudAusencia.Estado.RECHAZADO
            elif accion == 'devolver': 
                solicitud.estado = SolicitudAusencia.Estado.DEVUELTO
            
            solicitud.save()
            return redirect('solicitudes:lista_solicitudes')
            
    return render(request, 'solicitudes/responder_solicitudes.html', {
        'solicitud': solicitud, 
        'aprobaciones_previas': solicitud.aprobaciones.all().order_by('-fecha_accion')
    })

# creación de nueva solicitud y carga de adjuntos
@login_required
def crear_solicitud_view(request):
    if not hasattr(request.user, 'empleado'):
        messages.error(request, "No eres empleado.")
        return redirect('solicitudes:lista_solicitudes')

    empleado = request.user.empleado

    if request.method == 'POST':
        # obtenemos la lista de archivos manualmente
        archivos_raw = request.FILES.getlist('archivos_nuevos')
        
        form = SolicitudAusenciaForm(request.POST, request.FILES, empleado=empleado)
        
        if form.is_valid():
            try:
                nueva_solicitud = form.save(commit=False)
                nueva_solicitud.empresa = empleado.empresa
                nueva_solicitud.empleado = empleado
                nueva_solicitud.estado = SolicitudAusencia.Estado.PENDIENTE
                nueva_solicitud.save() 
                
                # guardar cada archivo en el modelo adjuntosolicitud
                for f in archivos_raw:
                    AdjuntoSolicitud.objects.create(solicitud=nueva_solicitud, archivo=f)
                
                messages.success(request, "Solicitud creada correctamente.")
                return redirect('solicitudes:vista_empleado')
            except Exception as e:
                messages.error(request, f"Error interno al guardar.")
        else:
            messages.error(request, "Error en el formulario. Verifique los datos.")
    else:
        form = SolicitudAusenciaForm(empleado=empleado)

    return render(request, 'solicitudes/crear_solicitud.html', {'form': form, 'es_edicion': False})

# edición de solicitud existente y adición de nuevos archivos
@login_required
def editar_solicitud_view(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudAusencia, pk=solicitud_id)
    
    if solicitud.empleado != request.user.empleado:
        return redirect('solicitudes:vista_empleado')
    
    if solicitud.estado not in [SolicitudAusencia.Estado.PENDIENTE, SolicitudAusencia.Estado.DEVUELTO]:
        messages.warning(request, "No puedes editar esta solicitud.")
        return redirect('solicitudes:vista_empleado')

    if request.method == 'POST':
        form = SolicitudAusenciaForm(request.POST, request.FILES, instance=solicitud, empleado=request.user.empleado)
        
        if form.is_valid():
            solicitud_editada = form.save(commit=False)
            solicitud_editada.estado = SolicitudAusencia.Estado.PENDIENTE 
            solicitud_editada.save()
            
            # añadir archivos nuevos sin borrar los anteriores
            archivos = request.FILES.getlist('archivos_nuevos')
            for f in archivos:
                AdjuntoSolicitud.objects.create(solicitud=solicitud_editada, archivo=f)
            
            messages.success(request, "Solicitud actualizada.")
            return redirect('solicitudes:vista_empleado')
        else:
            messages.error(request, "Error al editar.")
    else:
        form = SolicitudAusenciaForm(instance=solicitud, empleado=request.user.empleado)

    adjuntos_existentes = solicitud.adjuntos.all()
    return render(request, 'solicitudes/crear_solicitud.html', {
        'form': form, 
        'solicitud': solicitud, 
        'adjuntos_existentes': adjuntos_existentes, 
        'es_edicion': True
    })

# eliminación de la solicitud pendiente
@login_required
@require_POST
def eliminar_solicitud_view(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudAusencia, pk=solicitud_id)
    if solicitud.empleado == request.user.empleado and solicitud.estado in [SolicitudAusencia.Estado.PENDIENTE, SolicitudAusencia.Estado.DEVUELTO]:
        solicitud.delete()
        messages.success(request, "Solicitud eliminada.")
    else:
        messages.error(request, "No se puede eliminar.")
    return redirect('solicitudes:vista_empleado')

# eliminación de un archivo adjunto específico
@login_required
@require_POST
def eliminar_adjunto_ajax(request, adjunto_id):
    adjunto = get_object_or_404(AdjuntoSolicitud, pk=adjunto_id)
    
    if adjunto.solicitud.empleado != request.user.empleado:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    if adjunto.solicitud.estado not in [SolicitudAusencia.Estado.PENDIENTE, SolicitudAusencia.Estado.DEVUELTO]:
        return JsonResponse({'error': 'Bloqueado'}, status=403)
        
    try:
        adjunto.archivo.delete(save=False) 
        adjunto.delete()
        return JsonResponse({'status': 'ok', 'id': adjunto_id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# descarga del archivo adjunto
@login_required
def descargar_adjunto_view(request, adjunto_id): 
    adjunto = get_object_or_404(AdjuntoSolicitud, pk=adjunto_id)
    return FileResponse(adjunto.archivo)

# vista principal para administradores
@login_required
def lista_solicitudes_view(request):
    usuario = request.user
    
    es_jefe = (
        usuario.is_superuser or 
        getattr(usuario, 'es_admin_rrhh', False) or 
        getattr(usuario, 'es_superadmin_negocio', False)
    )

    if not es_jefe:
        return redirect('solicitudes:vista_empleado')

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

# listado de solicitudes propias del empleado
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