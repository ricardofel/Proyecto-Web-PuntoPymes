from django.db import models
# CORRECCIÓN 1: Quitamos 'source.' para evitar el ModuleNotFoundError
from empleados.models import Empleado  
from core.models import Empresa        

# 1. TIPO DE AUSENCIA
class TipoAusencia(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    # Estos campos aparecen en tu admin, así que deben estar aquí:
    afecta_sueldo = models.BooleanField(default=False)
    requiere_documento = models.BooleanField(default=False)
    descuenta_vacaciones = models.BooleanField(default=False)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

# 2. SOLICITUD DE AUSENCIA (Con estado 'Devuelto')
class SolicitudAusencia(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADO = 'aprobado', 'Aprobado'
        RECHAZADO = 'rechazado', 'Rechazado'
        DEVUELTO = 'devuelto', 'Devuelto (Subsanar)' # <--- NUEVO ESTADO

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='solicitudes')
    ausencia = models.ForeignKey(TipoAusencia, on_delete=models.PROTECT)
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_habiles = models.DecimalField(max_digits=5, decimal_places=1)
    motivo = models.TextField()
    adjunto_url = models.CharField(max_length=255, blank=True, null=True) 
    
    estado = models.CharField(
        max_length=20, 
        choices=Estado.choices, 
        default=Estado.PENDIENTE
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.empleado} - {self.ausencia}"

# 3. APROBACIÓN (Historial)
class AprobacionAusencia(models.Model):
    solicitud = models.ForeignKey(SolicitudAusencia, on_delete=models.CASCADE, related_name='aprobaciones')
    aprobador = models.ForeignKey(Empleado, on_delete=models.PROTECT)
    accion = models.CharField(max_length=20) 
    comentario = models.TextField(blank=True, null=True)
    fecha_accion = models.DateTimeField(auto_now_add=True)

# 4. REGISTRO DE VACACIONES (Restaurado para que tu admin no falle)
class RegistroVacaciones(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    periodo = models.CharField(max_length=50) # Ej: "2024-2025"
    dias_asignados = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    dias_tomados = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    @property
    def dias_disponibles(self):
        # Esta propiedad se usa en tu admin como readonly_field
        return self.dias_asignados - self.dias_tomados

    def __str__(self):
        return f"{self.empleado} - {self.periodo}"