import os
from django.db import models
from empleados.models import Empleado
from core.models import Empresa
from core.storage import private_storage

# --- UTILIDAD PARA RUTAS ---
def ruta_adjunto_solicitud(instance, filename):
    # Genera: solicitudes/empleado_00005/solicitud_10/documento.pdf
    # Organizamos por ID de empleado y luego por ID de solicitud
    folder_name = f"empleado_{instance.solicitud.empleado.id:05d}"
    subfolder = f"solicitud_{instance.solicitud.id}"
    return os.path.join('solicitudes', folder_name, subfolder, filename)

# 1. TIPO DE AUSENCIA 
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

# 2. SOLICITUD DE AUSENCIA
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
    
    # CAMBIO: Ahora es IntegerField (Entero)
    dias_habiles = models.IntegerField(default=0)
    
    motivo = models.TextField()
    
    # NOTA: Eliminamos 'archivo_adjunto' de aquí porque usaremos el modelo AdjuntoSolicitud
    
    estado = models.CharField(
        max_length=20, 
        choices=Estado.choices, 
        default=Estado.PENDIENTE
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.empleado} - {self.ausencia}"

# === NUEVO MODELO PARA MÚLTIPLES ARCHIVOS ===
class AdjuntoSolicitud(models.Model):
    solicitud = models.ForeignKey(
        SolicitudAusencia, 
        on_delete=models.CASCADE, 
        related_name='adjuntos' # Clave para acceder desde la solicitud: solicitud.adjuntos.all()
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

# 3. APROBACIÓN (Historial)
class AprobacionAusencia(models.Model):
    solicitud = models.ForeignKey(SolicitudAusencia, on_delete=models.CASCADE, related_name='aprobaciones')
    aprobador = models.ForeignKey(Empleado, on_delete=models.PROTECT)
    accion = models.CharField(max_length=20) 
    comentario = models.TextField(blank=True, null=True)
    fecha_accion = models.DateTimeField(auto_now_add=True)

# 4. REGISTRO DE VACACIONES
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