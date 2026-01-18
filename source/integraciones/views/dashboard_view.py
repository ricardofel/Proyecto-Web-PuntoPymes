from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from integraciones.models import IntegracionErp, Webhook, LogIntegracion
from usuarios.decorators import solo_superusuario
from integraciones.services.integracion_service import IntegracionService


@login_required
@solo_superusuario
def integraciones_dashboard_view(request):
    """
    Dashboard de integraciones.

    Muestra el estado de ERPs, webhooks y actividad reciente (logs).
    """
    erps = IntegracionErp.objects.all()
    webhooks = Webhook.objects.all()
    ultimos_logs = LogIntegracion.objects.all().order_by("-fecha")[:5]

    return render(
        request,
        "integraciones/dashboard.html",
        {
            "erps": erps,
            "webhooks": webhooks,
            "logs": ultimos_logs,
        },
    )


@login_required
@solo_superusuario
def logs_actualizados_view(request):
    """
    Partial para HTMX: refresca los logs más recientes.
    """
    ultimos_logs = LogIntegracion.objects.all().order_by("-fecha")[:10]

    return render(
        request,
        "integraciones/partials/logs_partial.html",
        {
            "logs": ultimos_logs,
        },
    )


@login_required
@solo_superusuario
def probar_conexion_erp_view(request, pk):
    """
    Ejecuta una prueba de conectividad (ping HTTP) contra el ERP configurado.
    """
    erp = get_object_or_404(IntegracionErp, pk=pk)

    if not erp.activo:
        messages.warning(request, "Integración pausada.")
        return redirect("integraciones:dashboard")

    exito, mensaje = IntegracionService.probar_conexion_erp(erp)

    if exito:
        messages.success(request, mensaje)
    else:
        messages.error(request, mensaje)

    return redirect("integraciones:dashboard")


@login_required
@solo_superusuario
def cambiar_estado_erp_view(request, pk):
    """
    Alterna el estado de la integración (activo/inactivo).
    """
    erp = get_object_or_404(IntegracionErp, pk=pk)

    erp.activo = not erp.activo
    erp.save()

    if erp.activo:
        messages.success(request, f"Integración {erp.nombre} HABILITADA.")
    else:
        messages.warning(request, f"Integración {erp.nombre} PAUSADA.")

    return redirect("integraciones:dashboard")


@login_required
@solo_superusuario
def probar_webhook_view(request, pk):
    """
    Envía un webhook de prueba desde el dashboard.
    """
    hook = get_object_or_404(Webhook, pk=pk)

    payload = {"evento": "TEST", "mensaje": "Prueba manual desde Dashboard"}
    codigo = IntegracionService.disparar_webhook(hook, payload)

    if 200 <= codigo < 300:
        messages.success(request, f"Webhook enviado (Código {codigo})")
    else:
        messages.error(request, f"Error al enviar (Código {codigo})")

    return redirect("integraciones:dashboard")
