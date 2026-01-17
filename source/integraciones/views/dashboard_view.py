import time
import requests 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from integraciones.models import IntegracionErp, Webhook, LogIntegracion
from usuarios.decorators import solo_superusuario
# --- 1. VISTA PRINCIPAL DEL DASHBOARD ---
@login_required
@solo_superusuario
def integraciones_dashboard_view(request):
    """
    Panel visual principal. Muestra el estado de ERPs, Webhooks y los últimos logs.
    """
    # Traemos las configuraciones
    erps = IntegracionErp.objects.all()
    webhooks = Webhook.objects.all()
    
    # Traemos los últimos 5 logs para mostrar actividad reciente al cargar la página
    ultimos_logs = LogIntegracion.objects.all().order_by('-fecha')[:5]

    return render(request, "integraciones/dashboard.html", {
        "erps": erps,
        "webhooks": webhooks,
        "logs": ultimos_logs
    })

# --- 2. VISTA PARA HTMX (LOGS EN VIVO) ---
@login_required
@solo_superusuario
def logs_actualizados_view(request):
    """
    Vista ligera llamada por HTMX cada 2 segundos para refrescar la terminal de logs.
    """
    # Traemos los últimos 10 logs (más recientes primero)
    ultimos_logs = LogIntegracion.objects.all().order_by('-fecha')[:10]
    
    return render(request, "integraciones/partials/logs_partial.html", {
        "logs": ultimos_logs
    })

# --- 3. VISTA DE PRUEBA REAL (PING HTTP) ---
@login_required
@solo_superusuario
def probar_conexion_erp_view(request, pk):
    erp = get_object_or_404(IntegracionErp, pk=pk)
    
    if not erp.activo:
        messages.warning(request, "Integración pausada.")
        return redirect('integraciones:dashboard')

    # Usamos el servicio
    exito, mensaje = IntegracionService.probar_conexion_erp(erp)
    
    if exito:
        messages.success(request, mensaje)
    else:
        messages.error(request, mensaje)
        
    return redirect('integraciones:dashboard')

# --- 4. VISTA DE INTERRUPTOR (HABILITAR/PAUSAR) ---
@login_required
@solo_superusuario
def cambiar_estado_erp_view(request, pk):
    """
    Interruptor LÓGICO: Habilita o deshabilita el uso de la integración.
    """
    erp = get_object_or_404(IntegracionErp, pk=pk)
    
    # Invertimos el permiso
    erp.activo = not erp.activo
    erp.save()
    
    if erp.activo:
        messages.success(request, f"Integración {erp.nombre} HABILITADA.")
    else:
        messages.warning(request, f"Integración {erp.nombre} PAUSADA.")
        
    return redirect('integraciones:dashboard')

# --- 5. VISTA PARA PROBAR WEBHOOKS (REAL) ---
@login_required
@solo_superusuario
def probar_webhook_view(request, pk):
    hook = get_object_or_404(Webhook, pk=pk)
    
    payload = {"evento": "TEST", "mensaje": "Prueba manual desde Dashboard"}
    
    # Usamos el servicio
    codigo = IntegracionService.disparar_webhook(hook, payload)
    
    if 200 <= codigo < 300:
        messages.success(request, f"Webhook enviado (Código {codigo})")
    else:
        messages.error(request, f"Error al enviar (Código {codigo})")

    return redirect('integraciones:dashboard')