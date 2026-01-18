from django.db.models.signals import post_save
from django.dispatch import receiver

from solicitudes.models import SolicitudAusencia
from asistencia.models import EventoAsistencia

from .models import Webhook
from .constants import EventosWebhook
from .services.integracion_service import IntegracionService


@receiver(post_save, sender=SolicitudAusencia)
def webhook_nuevo_permiso(sender, instance, created, **kwargs):
    """
    Dispara webhooks activos cuando se crea una nueva solicitud de ausencia.
    """
    if not created:
        return

    hooks = Webhook.objects.filter(
        evento=EventosWebhook.SOLICITUD_APROBADA,
        activo=True,
    )

    payload = {
        "evento": "NUEVA_SOLICITUD",
        "empleado": str(instance.empleado),
        "tipo": str(instance.ausencia),
        "desde": str(instance.fecha_inicio),
        "hasta": str(instance.fecha_fin),
    }

    for hook in hooks:
        IntegracionService.disparar_webhook(hook, payload)


@receiver(post_save, sender=EventoAsistencia)
def webhook_check_in(sender, instance, created, **kwargs):
    """
    Placeholder para futuros webhooks de eventos de asistencia.
    """
    pass
