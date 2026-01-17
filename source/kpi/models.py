from decimal import Decimal
from django.db import models
from kpi.constants import CodigosKPI # Importamos

class KPI(models.Model):
    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey("core.Empresa", on_delete=models.CASCADE)
    
    nombre = models.CharField(max_length=100)
    # Nuevo campo clave para la lógica
    codigo = models.CharField(
        max_length=50, 
        choices=CodigosKPI.OPCIONES, 
        default=CodigosKPI.MANUAL,
        help_text="Determina la lógica de cálculo automático"
    )
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=20)
    frecuencia = models.CharField(max_length=20)
    meta_default = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kpi"
        verbose_name = "KPI"
        verbose_name_plural = "KPIs"

    def __str__(self):
        return f"{self.nombre} ({self.unidad_medida})"

class KPIResultado(models.Model):
    id = models.BigAutoField(primary_key=True)
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE, related_name="resultados")
    
    # ... resto de campos igual ...
    periodo = models.CharField(max_length=20)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    meta_periodo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    calculado_automatico = models.BooleanField(default=False)
    observacion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kpi_resultado"
        ordering = ['-periodo'] # Orden por defecto útil
        constraints = [
            models.UniqueConstraint(
                fields=["kpi", "periodo"], # Simplificado si es por empresa global
                name="unique_kpi_periodo"
            )
        ]