import os
from django.db import models
from empleados.models import Empleado
from core.models import Empresa
from core.storage import private_storage

# utilidad para generar ruta de archivo basada en empleado y solicitud
def ruta_adjunto_solicitud(instance, filename):
    folder_name = f"empleado_{instance.solicitud.empleado.id:05d}"
    subfolder = f"solicitud_{instance.solicitud.id}"
    return os.path.join('solicitudes', folder_name, subfolder, filename)

# modelo para configurar tipos de ausencia y sus reglas
class TipoAusencia(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    afecta_sueldo = models.BooleanField(default=False)
    requiere_documento = models.BooleanField(default=False)
    descuenta_vacaciones = models.BooleanField(default=False)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

# modelo principal para registrar solicitudes de ausencia
class SolicitudAusencia(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADO = 'aprobado', 'Aprobado'
        RECHAZADO = 'rechazado', 'Rechazado'
        DEVUELTO = 'devuelto', 'Devuelto (Subsanar)'

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='solicitudes')
    ausencia = models.ForeignKey(TipoAusencia, on_delete=models.PROTECT)
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    dias_habiles = models.IntegerField(default=0)
    
    motivo = models.TextField()
    
    estado = models.CharField(
        max_length=20, 
        choices=Estado.choices, 
        default=Estado.PENDIENTE
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.empleado} - {self.ausencia}"

# modelo para almacenar múltiples archivos adjuntos vinculados a una solicitud
class AdjuntoSolicitud(models.Model):
    solicitud = models.ForeignKey(
        SolicitudAusencia, 
        on_delete=models.CASCADE, 
        related_name='adjuntos'
    )
    archivo = models.FileField(
        upload_to=ruta_adjunto_solicitud,
        storage=private_storage,
        verbose_name="Documento"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return os.path.basename(self.archivo.name)

    def __str__(self):
        return f"Adjunto {self.filename()} para Solicitud {self.solicitud.id}"

# historial de acciones de aprobación o rechazo
class AprobacionAusencia(models.Model):
    solicitud = models.ForeignKey(SolicitudAusencia, on_delete=models.CASCADE, related_name='aprobaciones')
    aprobador = models.ForeignKey(Empleado, on_delete=models.PROTECT)
    accion = models.CharField(max_length=20) 
    comentario = models.TextField(blank=True, null=True)
    fecha_accion = models.DateTimeField(auto_now_add=True)

# control de saldos de vacaciones por empleado y periodo
class RegistroVacaciones(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    periodo = models.CharField(max_length=50)
    dias_asignados = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    dias_tomados = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    @property
    def dias_disponibles(self):
        return self.dias_asignados - self.dias_tomados

    def __str__(self):
        return f"{self.empleado} - {self.periodo}"