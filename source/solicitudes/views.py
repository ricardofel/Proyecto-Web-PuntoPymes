from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST 


from .models import SolicitudAusencia, AprobacionAusencia, TipoAusencia 
from .forms import AprobacionForm


@login_required
def lista_solicitudes_view(request):
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



@login_required
def responer_solicitudes_view(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudAusencia, pk=solicitud_id)
    
    try:
        aprobador = request.user.empleado 
    except AttributeError:
        messages.error(request, "Error: Tu usuario no tiene un perfil de Empleado asociado.")
        return redirect('solicitudes:lista_solicitudes')
    
    if request.method == 'POST':
        form = AprobacionForm(request.POST)
        
        if form.is_valid():
            
            aprobacion = form.save(commit=False)
            aprobacion.solicitud = solicitud
            aprobacion.aprobador = aprobador
            aprobacion.save()

            
            if aprobacion.accion == 'aprobar':
                solicitud.estado = SolicitudAusencia.Estado.APROBADO
            elif aprobacion.accion == 'rechazar':
                solicitud.estado = SolicitudAusencia.Estado.RECHAZADO
            
           
            solicitud.save()
            
           
            verb = "aprobada" if solicitud.estado == SolicitudAusencia.Estado.APROBADO else "rechazada"
            messages.success(request, f"La solicitud ha sido {verb} correctamente.")
            
            return redirect('solicitudes:lista_solicitudes')
        else:
            messages.error(request, f"Error al procesar: {form.errors}")
    else:
        form = AprobacionForm()

    context = {
        'solicitud': solicitud,
        'form': form,
        'aprobaciones_previas': solicitud.aprobaciones.all().order_by('-fecha_accion')
    }
    return render(request, 'solicitudes/responder_solicitudes.html', context)



@login_required
def empleado_view(request):
    """
    Muestra solo las solicitudes creadas por el usuario logueado.
    """
    
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



@login_required
def crear_solicitud_view(request):

    if not hasattr(request.user, 'empleado'):
        messages.error(request, "No puedes crear solicitudes porque tu usuario no es un Empleado.")
        return redirect('solicitudes:lista_solicitudes')

    empleado = request.user.empleado

    if request.method == 'POST':

        try:
            # Capturamos los datos del HTML
            ausencia_id = request.POST.get('ausencia')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            dias_habiles = request.POST.get('dias_habiles')
            motivo = request.POST.get('motivo')
            

            if not all([ausencia_id, fecha_inicio, fecha_fin, dias_habiles, motivo]):
                messages.error(request, "Por favor completa todos los campos obligatorios.")
            else:

                nueva_solicitud = SolicitudAusencia(
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
                    nueva_solicitud.adjunto_url = request.FILES['adjunto'].name 
                
                nueva_solicitud.save()
                
                messages.success(request, "Solicitud enviada correctamente.")
                return redirect('solicitudes:vista_empleado') 

        except Exception as e:
            messages.error(request, f"Ocurrió un error al guardar: {e}")


    tipos_ausencia = TipoAusencia.objects.filter(empresa=empleado.empresa, estado=True)

    return render(request, 'solicitudes/crear_solicitud.html', {
        'tipos_ausencia': tipos_ausencia
    })



@login_required
def editar_solicitud_view(request, solicitud_id):

    solicitud = get_object_or_404(SolicitudAusencia, pk=solicitud_id)
    

    if solicitud.empleado != request.user.empleado:
        messages.error(request, "No tienes permiso para editar esta solicitud.")
        return redirect('solicitudes:vista_empleado')


    if solicitud.estado != SolicitudAusencia.Estado.PENDIENTE:
        messages.warning(request, "No puedes editar una solicitud que ya fue procesada.")
        return redirect('solicitudes:vista_empleado')

    if request.method == 'POST':
        try:

            solicitud.ausencia_id = request.POST.get('ausencia')
            solicitud.fecha_inicio = request.POST.get('fecha_inicio')
            solicitud.fecha_fin = request.POST.get('fecha_fin')
            solicitud.dias_habiles = request.POST.get('dias_habiles')
            solicitud.motivo = request.POST.get('motivo')
            
            if 'adjunto' in request.FILES:
                solicitud.adjunto_url = request.FILES['adjunto'].name 
            
            solicitud.save()
            messages.success(request, "Solicitud actualizada correctamente.")
            return redirect('solicitudes:vista_empleado')

        except Exception as e:
            messages.error(request, f"Error al actualizar: {e}")


    empleado = request.user.empleado
    tipos_ausencia = TipoAusencia.objects.filter(empresa=empleado.empresa, estado=True)

    return render(request, 'solicitudes/crear_solicitud.html', {
        'tipos_ausencia': tipos_ausencia,
        'solicitud': solicitud,  
        'es_edicion': True
    })



@login_required
@require_POST 
def eliminar_solicitud_view(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudAusencia, pk=solicitud_id)
    

    if solicitud.empleado != request.user.empleado:
        messages.error(request, "No tienes permiso para eliminar esta solicitud.")
        return redirect('solicitudes:vista_empleado')
    

    if solicitud.estado != SolicitudAusencia.Estado.PENDIENTE:
        messages.error(request, "No se puede eliminar una solicitud ya procesada.")
        return redirect('solicitudes:vista_empleado')

    solicitud.delete()
    messages.success(request, "Solicitud eliminada correctamente.")
    return redirect('solicitudes:vista_empleado')