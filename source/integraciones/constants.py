class EstadoIntegracion:
    """
    Estados posibles de una integración externa (ERP, servicios, etc.).
    Se utiliza para reflejar el resultado de la última sincronización.
    """
    EXITOSO = 'ok'
    ERROR = 'error'

    # Opciones para usar como choices en modelos Django
    OPCIONES = [
        (EXITOSO, 'Exitoso'),
        (ERROR, 'Error'),
    ]


class EventosWebhook:
    """
    Eventos del sistema que pueden disparar webhooks externos.
    Estos valores se usan como identificadores técnicos (no textos de UI).
    """
    EMPLEADO_CREADO = 'empleado_creado'
    SOLICITUD_APROBADA = 'solicitud_aprobada'
    ALERTA_KPI = 'alerta_kpi'

    # Opciones legibles para administración / configuración
    OPCIONES = [
        (EMPLEADO_CREADO, 'Nuevo Empleado'),
        (SOLICITUD_APROBADA, 'Vacaciones Aprobadas'),
        (ALERTA_KPI, 'Alerta de KPI Bajo'),
    ]
