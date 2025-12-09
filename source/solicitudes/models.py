from decimal import Decimal
from django.db import models
from django.utils import timezone # 📌 ¡IMPORTANTE! Nueva importación
from django.utils.translation import gettext_lazy as _


class TipoAusencia(models.Model):
    # Tabla ausencia
    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey("core.Empresa", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    afecta_sueldo = models.BooleanField(default=False)
    requiere_documento = models.BooleanField(default=False)
    descuenta_vacaciones = models.BooleanField(default=False)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ausencia"

    def __str__(self):
        return str(self.nombre)


class RegistroVacaciones(models.Model):
    # Tabla registro_vacaciones
    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey("core.Empresa", on_delete=models.CASCADE)
    empleado = models.ForeignKey(
        "empleados.Empleado", on_delete=models.CASCADE, related_name="saldos_vacaciones"
    )
    periodo = models.CharField(max_length=20, help_text=_("Ciclo fiscal"))
    dias_asignados = models.DecimalField(max_digits=5, decimal_places=2)
    dias_tomados = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal(0)
    )
    dias_disponibles = models.DecimalField(max_digits=5, decimal_places=2)

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "registro_vacaciones"
        constraints = [
            models.UniqueConstraint(
                fields=["empleado", "periodo"], name="unique_saldo_periodo"
            )
        ]

    def __str__(self):
        return f"Vacaciones {self.empleado} ({self.periodo})"


class SolicitudAusencia(models.Model):
    # Tabla solicitud_ausencia
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", _("Pendiente")
        APROBADO = "aprobado", _("Aprobado")
        RECHAZADO = "rechazado", _("Rechazado")
        CANCELADO = "cancelado", _("Cancelado")

    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey("core.Empresa", on_delete=models.CASCADE)
    empleado = models.ForeignKey(
        "empleados.Empleado", on_delete=models.CASCADE, related_name="solicitudes"
    )
    ausencia = models.ForeignKey(TipoAusencia, on_delete=models.PROTECT)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_habiles = models.DecimalField(max_digits=5, decimal_places=2)
    motivo = models.TextField()
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    adjunto_url = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "solicitud_ausencia"

    def __str__(self):
        return f"{self.ausencia} - {self.empleado}"


class AprobacionAusencia(models.Model):
    # Tabla aprobacion_ausencia
    
    class AccionChoices(models.TextChoices):
        APROBAR = "aprobar", _("Aprobar")
        RECHAZAR = "rechazar", _("Rechazar")
        
    id = models.BigAutoField(primary_key=True)
    solicitud = models.ForeignKey(
        SolicitudAusencia, on_delete=models.CASCADE, related_name="aprobaciones"
    )
    aprobador = models.ForeignKey("empleados.Empleado", on_delete=models.PROTECT)
    
    accion = models.CharField(
        max_length=20, 
        choices=AccionChoices.choices, 
        default=AccionChoices.APROBAR,
        help_text=_("Aprobar o rechazar la solicitud")
    ) 
    
    # 📌 CAMBIO CLAVE: Usamos default=timezone.now en lugar de auto_now_add=True
    fecha_accion = models.DateTimeField(default=timezone.now) 
    comentario = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "aprobacion_ausencia"