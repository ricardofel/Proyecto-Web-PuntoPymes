from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from .models import SolicitudAusencia, AprobacionAusencia
from .forms import AprobacionForm

def lista_solicitudes_view(request):
    solicitudes = SolicitudAusencia.objects.all().order_by('-fecha_creacion')
    query = request.GET.get('q')
    if query:
        solicitudes = solicitudes.filter(
            Q(empleado__nombre__icontains=query) | 
            Q(ausencia__nombre__icontains=query) |
            Q(motivo__icontains=query)
        ).distinct()
    return render(request, 'solicitudes/lista_solicitudes.html', {'solicitudes': solicitudes, 'query': query})


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
            # 1. Guardar la Aprobación (que usa 'aprobar' o 'rechazar')
            aprobacion = form.save(commit=False)
            aprobacion.solicitud = solicitud
            aprobacion.aprobador = aprobador
            aprobacion.save()

            # 2. 📌 TRADUCCIÓN DE ESTADOS (CAMBIO CLAVE)
            # Como tu modelo Aprobacion usa verbos ('aprobar') y Solicitud usa participios ('aprobado'),
            # hacemos el mapeo manualmente aquí.
            
            if aprobacion.accion == 'aprobar':
                solicitud.estado = SolicitudAusencia.Estado.APROBADO # Equivale a 'aprobado'
            elif aprobacion.accion == 'rechazar':
                solicitud.estado = SolicitudAusencia.Estado.RECHAZADO # Equivale a 'rechazado'
            
            # Guardamos el cambio en la solicitud principal
            solicitud.save()
            
            # Mensaje de éxito
            verb = "aprobada" if solicitud.estado == 'aprobado' else "rechazada"
            messages.success(request, f"La solicitud ha sido {verb} correctamente.")
            
            return redirect('solicitudes:lista_solicitudes')
        else:
            # Si falla la validación, mostramos el error
            messages.error(request, f"Error al procesar: {form.errors}")
    else:
        form = AprobacionForm()

    context = {
        'solicitud': solicitud,
        'form': form,
        'aprobaciones_previas': solicitud.aprobaciones.all().order_by('-fecha_accion')
    }
    return render(request, 'solicitudes/responder_solicitudes.html', context)

# Vistas placeholder
def crear_solicitud_view(request): return render(request, 'solicitudes/crear_solicitud.html', {})
def empleado_view(request): return render(request, 'solicitudes/solicitudes_empleado.html', {})