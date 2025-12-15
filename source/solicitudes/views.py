from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST # Importante para la seguridad al eliminar

# Importamos TipoAusencia para poder llenar el select del formulario
from .models import SolicitudAusencia, AprobacionAusencia, TipoAusencia 
from .forms import AprobacionForm

# ---------------------------------------------------------
# 1. VISTA DE ADMINISTRADOR / RRHH (Ver todas)
# ---------------------------------------------------------
@login_required
def lista_solicitudes_view(request):
    solicitudes = SolicitudAusencia.objects.all().order_by('-fecha_creacion')
    query = request.GET.get('q')
    
    if query:
        solicitudes = solicitudes.filter(
            Q(empleado__nombres__icontains=query) | # Asumiendo campo 'nombres' en Empleado
            Q(empleado__apellidos__icontains=query) |
            Q(ausencia__nombre__icontains=query) |
            Q(motivo__icontains=query)
        ).distinct()
        
    return render(request, 'solicitudes/lista_solicitudes.html', {'solicitudes': solicitudes, 'query': query})


# ---------------------------------------------------------
# 2. VISTA PARA RESPONDER (Aprobar/Rechazar)
# ---------------------------------------------------------
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
            # 1. Guardar la Aprobación
            aprobacion = form.save(commit=False)
            aprobacion.solicitud = solicitud
            aprobacion.aprobador = aprobador
            aprobacion.save()

            # 2. TRADUCCIÓN DE ESTADOS
            if aprobacion.accion == 'aprobar':
                solicitud.estado = SolicitudAusencia.Estado.APROBADO
            elif aprobacion.accion == 'rechazar':
                solicitud.estado = SolicitudAusencia.Estado.RECHAZADO
            
            # Guardamos el cambio en la solicitud principal
            solicitud.save()
            
            # Mensaje de éxito
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


# ---------------------------------------------------------
# 3. VISTA DE EMPLEADO (Mis Solicitudes)
# ---------------------------------------------------------
@login_required
def empleado_view(request):
    """
    Muestra solo las solicitudes creadas por el usuario logueado.
    """
    # 1. Seguridad: Verificar si el usuario tiene un empleado vinculado
    if not hasattr(request.user, 'empleado'):
        # Si es un admin puro sin ficha de empleado, mostramos lista vacía
        return render(request, 'solicitudes/solicitudes_empleado.html', {'solicitudes': []})

    # 2. Obtenemos SU empleado
    empleado_actual = request.user.empleado

    # 3. Filtramos: Solo las solicitudes donde empleado = empleado_actual
    solicitudes = SolicitudAusencia.objects.filter(empleado=empleado_actual).order_by('-fecha_creacion')

    # 4. Lógica de Búsqueda
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
# 4. VISTA CREAR SOLICITUD
# ---------------------------------------------------------
@login_required
def crear_solicitud_view(request):
    # 1. Seguridad: Verificar que sea empleado
    if not hasattr(request.user, 'empleado'):
        messages.error(request, "No puedes crear solicitudes porque tu usuario no es un Empleado.")
        return redirect('solicitudes:lista_solicitudes')

    empleado = request.user.empleado

    if request.method == 'POST':
        # 2. Procesar el Formulario
        try:
            # Capturamos los datos del HTML
            ausencia_id = request.POST.get('ausencia')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            dias_habiles = request.POST.get('dias_habiles')
            motivo = request.POST.get('motivo')
            
            # Validación básica
            if not all([ausencia_id, fecha_inicio, fecha_fin, dias_habiles, motivo]):
                messages.error(request, "Por favor completa todos los campos obligatorios.")
            else:
                # 3. Crear la Solicitud
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

    # 4. GET: Cargar los datos para el select
    tipos_ausencia = TipoAusencia.objects.filter(empresa=empleado.empresa, estado=True)

    return render(request, 'solicitudes/crear_solicitud.html', {
        'tipos_ausencia': tipos_ausencia
    })


# ---------------------------------------------------------
# 5. EDITAR SOLICITUD (NUEVA)
# ---------------------------------------------------------
@login_required
def editar_solicitud_view(request, solicitud_id):
    # 1. Obtener solicitud y verificar permisos
    solicitud = get_object_or_404(SolicitudAusencia, pk=solicitud_id)
    
    # Solo el dueño puede editar
    if solicitud.empleado != request.user.empleado:
        messages.error(request, "No tienes permiso para editar esta solicitud.")
        return redirect('solicitudes:vista_empleado')

    # Solo se edita si está pendiente
    if solicitud.estado != SolicitudAusencia.Estado.PENDIENTE:
        messages.warning(request, "No puedes editar una solicitud que ya fue procesada.")
        return redirect('solicitudes:vista_empleado')

    if request.method == 'POST':
        try:
            # 2. Actualizar datos desde el form
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

    # 3. Cargar datos para el formulario en modo edición
    empleado = request.user.empleado
    tipos_ausencia = TipoAusencia.objects.filter(empresa=empleado.empresa, estado=True)

    return render(request, 'solicitudes/crear_solicitud.html', {
        'tipos_ausencia': tipos_ausencia,
        'solicitud': solicitud,  # Activa el modo edición en el template
        'es_edicion': True
    })


# ---------------------------------------------------------
# 6. ELIMINAR SOLICITUD (NUEVA)
# ---------------------------------------------------------
@login_required
@require_POST # Seguridad: solo acepta peticiones tipo POST (submit del form)
def eliminar_solicitud_view(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudAusencia, pk=solicitud_id)
    
    # Solo el dueño puede eliminar
    if solicitud.empleado != request.user.empleado:
        messages.error(request, "No tienes permiso para eliminar esta solicitud.")
        return redirect('solicitudes:vista_empleado')
    
    # Solo se elimina si está pendiente
    if solicitud.estado != SolicitudAusencia.Estado.PENDIENTE:
        messages.error(request, "No se puede eliminar una solicitud ya procesada.")
        return redirect('solicitudes:vista_empleado')

    solicitud.delete()
    messages.success(request, "Solicitud eliminada correctamente.")
    return redirect('solicitudes:vista_empleado')