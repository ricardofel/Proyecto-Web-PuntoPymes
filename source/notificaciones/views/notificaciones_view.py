from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from notificaciones.models import Notificacion

@login_required
def lista_notificaciones(request):
    """
    Muestra todas las notificaciones del usuario actual.
    """
    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).order_by('-fecha_creacion')
    
    # Usamos 'leido' (masculino)
    no_leidas = notificaciones.filter(leido=False).count()

    return render(request, "notificaciones/lista.html", {
        "notificaciones": notificaciones,
        "no_leidas": no_leidas
    })

@login_required
def marcar_una_leida(request, pk):
    notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    
    if not notificacion.leido:
        notificacion.leido = True
        notificacion.save()
        messages.success(request, "Notificación marcada como leída.")
    
    return redirect("notificaciones:lista_notificaciones")

@login_required
def marcar_todas_leidas(request):
    # Usamos 'leido' (masculino)
    Notificacion.objects.filter(usuario=request.user, leido=False).update(leido=True)
    messages.success(request, "Todas marcadas como leídas.")
    
    return redirect("notificaciones:lista_notificaciones")

@login_required
def ver_detalle_notificacion(request, pk):
    """
    Muestra la ficha completa de una notificación usando el template genérico.
    """
    notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    
    # Al entrar al detalle, la marcamos como leída automáticamente
    if not notificacion.leido:
        notificacion.leido = True
        notificacion.save()

    # Preparamos la lista de detalles para el template genérico
    detalles = [
        {'label': 'Título', 'valor': notificacion.titulo},
        {'label': 'Mensaje Completo', 'valor': notificacion.mensaje},
        {'label': 'Tipo de Aviso', 'valor': notificacion.get_tipo_display()}, # Muestra "Éxito" en vez de "success"
        {'label': 'Fecha de Recepción', 'valor': notificacion.fecha_creacion},
        {'label': 'Estado', 'valor': "Leída" if notificacion.leido else "No leída"},
        {'label': 'Enlace de Acción', 'valor': notificacion.url_destino if notificacion.url_destino else "Sin enlace"},
    ]

    return render(request, 'notificaciones/detalle.html', {
        'titulo': 'Detalle de Notificación',
        'objeto_str': notificacion.titulo,
        'detalles': detalles,
        # 'back_url' se maneja en el template con request.GET.next o default
    })