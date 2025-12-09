# solicitudes/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages # Añadido para manejo de mensajes de éxito
from .models import SolicitudAusencia, AprobacionAusencia 
from .forms import AprobacionForm 

# --- Vista para Listar Solicitudes (lista_solicitudes.html) ---
def lista_solicitudes_view(request): # Cambiado a lista_solicitudes_view para sincronizar con urls.py
    """Muestra todas las solicitudes para el administrador/gestor."""
    
    # Carga todas las solicitudes ordenadas por fecha de creación (más recientes primero)
    solicitudes = SolicitudAusencia.objects.all().order_by('-fecha_creacion')
    
    query = request.GET.get('q')
    if query:
        # Implementación de búsqueda simple (ajusta los campos según tu modelo Empleado)
        solicitudes = solicitudes.filter(
            Q(empleado__nombre__icontains=query) | 
            Q(ausencia__nombre__icontains=query) |
            Q(motivo__icontains=query)
        ).distinct()

    context = {
        'solicitudes': solicitudes,
        'query': query,
    }
    return render(request, 'solicitudes/lista_solicitudes.html', context)


# --- Vista para Responder/Gestionar Solicitud (responder_solicitudes.html) ---
def responer_solicitudes_view(request, solicitud_id): # Cambiado a responer_solicitudes_view para sincronizar
    """Permite al aprobador aprobar o rechazar una solicitud."""
    
    solicitud = get_object_or_404(SolicitudAusencia, pk=solicitud_id)
    
    # Asumo que tienes una forma de obtener el empleado aprobador actual (request.user.empleado)
    # ¡Asegúrate de que esta línea no falle si el usuario no tiene perfil de empleado!
    try:
        aprobador = request.user.empleado 
    except AttributeError:
        messages.error(request, "Error: El usuario no está asociado a un Empleado.")
        return redirect('solicitudes:lista_solicitudes')
    
    if request.method == 'POST':
        # Asumo que usarás un formulario de modelo para crear AprobacionAusencia
        form = AprobacionForm(request.POST) 
        if form.is_valid():
            aprobacion = form.save(commit=False)
            aprobacion.solicitud = solicitud
            aprobacion.aprobador = aprobador
            aprobacion.save()

            # Actualizar el estado de la solicitud principal
            solicitud.estado = aprobacion.accion # 'aprobar' o 'rechazar'
            solicitud.save()
            
            messages.success(request, f"Solicitud #{solicitud.id} ha sido {aprobacion.get_accion_display()} correctamente.")
            return redirect('solicitudes:lista_solicitudes') # Redirige a la lista
    else:
        # Pasa un formulario de Aprobacion vacío
        form = AprobacionForm()

    context = {
        'solicitud': solicitud,
        'form': form,
        'aprobaciones_previas': solicitud.aprobaciones.all().order_by('-fecha_accion')
    }
    return render(request, 'solicitudes/responder_solicitudes.html', context)
    
def crear_solicitud_view(request):
    # Por ahora solo carga el template vacío
    return render(request, 'solicitudes/crear_solicitud.html', {})

def empleado_view(request):
    # Por ahora solo carga el template vacío
    return render(request, 'solicitudes/solicitudes_empleado.html', {})