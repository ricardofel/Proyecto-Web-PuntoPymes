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
    """
    Realiza un PING REAL (HTTP GET) al servidor externo.
    """
    erp = get_object_or_404(IntegracionErp, pk=pk)
    
    # Si la integración está PAUSADA (inactiva), no permitimos probar conexión
    if not erp.activo:
        messages.warning(request, f"La integración con {erp.nombre} está pausada. Actívela primero.")
        return redirect('integraciones:dashboard')

    # URL real configurada en la base de datos
    url = erp.url_api
    
    try:
        # 1. Petición REAL a internet
        # Timeout de 5 segundos para no colgar el servidor si no responde
        response = requests.get(url, timeout=5)
        
        # 2. Análisis de la respuesta real
        status_code = response.status_code
        
        # Consideramos éxito si el servidor responde (incluso 401/403 significa que está vivo)
        if 200 <= status_code < 500:
            erp.estado_sincronizacion = 'ok'
            erp.fecha_ultima_sincronizacion = timezone.now()
            erp.save()
            
            LogIntegracion.objects.create(
                integracion=erp,
                endpoint=url,
                codigo_respuesta=status_code,
                mensaje_respuesta=f"Conexión exitosa. Tiempo respuesta: {response.elapsed.total_seconds()}s"
            )
            messages.success(request, f"Servidor respondió correctamente (Código {status_code}).")
            
        else:
            # El servidor dio error interno (500+)
            raise Exception(f"Servidor devolvió error interno {status_code}")

    except requests.exceptions.RequestException as e:
        # 3. Captura de errores REALES (Sin internet, URL mal escrita, DNS fallido)
        erp.estado_sincronizacion = 'error'
        erp.save()
        
        mensaje_error = f"Fallo de conexión: {str(e)}"
        
        LogIntegracion.objects.create(
            integracion=erp,
            endpoint=url,
            codigo_respuesta=0, # 0 indica que no hubo respuesta HTTP
            mensaje_respuesta=mensaje_error[:200] # Cortamos si es muy largo
        )
        messages.error(request, f"No se pudo conectar con {erp.nombre}. Verifique la URL.")
        
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
    """
    Envía un payload JSON de prueba a la URL destino del Webhook.
    """
    webhook = get_object_or_404(Webhook, pk=pk)
    
    if not webhook.activo:
        messages.warning(request, f"El webhook {webhook.nombre} está inactivo.")
        return redirect('integraciones:dashboard')

    # Datos de prueba simulando un evento real
    payload = {
        "evento": webhook.evento,
        "timestamp": timezone.now().isoformat(),
        "sistema_origen": "Talent Track RRHH",
        "datos": {
            "empleado": "Tony Stark",
            "accion": "Contratación",
            "departamento": "Ingeniería",
            "mensaje": "Se ha registrado un nuevo ingreso en el sistema."
        }
    }

    try:
        # 1. Disparo REAL a internet (POST request)
        response = requests.post(webhook.url_destino, json=payload, timeout=5)
        
        # 2. Registrar el intento
        LogIntegracion.objects.create(
            webhook=webhook, # Asegúrate que tu modelo Log tenga este campo, si no, usa 'endpoint'
            endpoint=webhook.url_destino,
            codigo_respuesta=response.status_code,
            mensaje_respuesta=f"Webhook disparado. Respuesta: {response.text[:100]}"
        )
        
        if 200 <= response.status_code < 300:
            messages.success(request, f"Evento enviado exitosamente a {webhook.nombre} (Code {response.status_code})")
        else:
            messages.warning(request, f"El servidor remoto recibió el evento pero respondió con error: {response.status_code}")

    except requests.exceptions.RequestException as e:
        LogIntegracion.objects.create(
            endpoint=webhook.url_destino,
            codigo_respuesta=0,
            mensaje_respuesta=f"Fallo envío Webhook: {str(e)}"
        )
        messages.error(request, f"No se pudo enviar el evento. Verifique la URL.")

    return redirect('integraciones:dashboard')