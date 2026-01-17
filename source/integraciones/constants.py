class EstadoIntegracion:
    EXITOSO = 'ok'
    ERROR = 'error'
    
    OPCIONES = [
        (EXITOSO, 'Exitoso'),
        (ERROR, 'Error'),
    ]

class EventosWebhook:
    EMPLEADO_CREADO = 'empleado_creado'
    SOLICITUD_APROBADA = 'solicitud_aprobada'
    ALERTA_KPI = 'alerta_kpi'
    
    OPCIONES = [
        (EMPLEADO_CREADO, 'Nuevo Empleado'),
        (SOLICITUD_APROBADA, 'Vacaciones Aprobadas'),
        (ALERTA_KPI, 'Alerta de KPI Bajo'),
    ]