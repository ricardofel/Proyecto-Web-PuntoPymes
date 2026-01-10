from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _

# CAMBIO: Renombrado de 'Kpi' a 'KPI' (Mayúsculas)
class KPI(models.Model):
    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey("core.Empresa", on_delete=models.CASCADE)
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=20)
    frecuencia = models.CharField(max_length=20)
    formula = models.TextField(blank=True, null=True)
    meta_default = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kpi"
        verbose_name = "KPI"
        verbose_name_plural = "KPIs"

    def __str__(self):
        return f"{self.nombre} ({self.unidad_medida})"

# CAMBIO: Renombrado de 'KpiResultado' a 'KPIResultado'
class KPIResultado(models.Model):
    id = models.BigAutoField(primary_key=True)
    # Referencia a la clase KPI corregida
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE, related_name="resultados")
    
    empleado = models.ForeignKey(
        "empleados.Empleado", 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name="kpi_resultados"
    )
    
    periodo = models.CharField(max_length=20)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    meta_periodo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    calculado_automatico = models.BooleanField(default=False)
    observacion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kpi_resultado"
        constraints = [
            models.UniqueConstraint(
                fields=["kpi", "empleado", "periodo"], 
                name="unique_kpi_periodo_empleado"
            )
        ]

    def __str__(self):
        entidad = self.empleado if self.empleado else "Global"
        return f"{self.kpi.nombre} - {self.periodo}: {self.valor}"