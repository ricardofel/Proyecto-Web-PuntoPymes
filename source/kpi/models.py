from django.db import models
from django.utils.translation import gettext_lazy as _

"""
Modelos de la app kpi (Indicadores de Desempeño):

- KPI (Definición del indicador - Tabla 12)
- KPIResultado (Resultados por empleado y periodo - Tabla 13)

Ver diccionario de datos Tablas 12 y 13.
"""


class KPI(models.Model):
    # Tabla kpi
    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey("core.Empresa", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=20, help_text=_("%, USD, Puntos"))
    frecuencia = models.CharField(max_length=20, help_text=_("mensual, trimestral"))
    formula = models.TextField(blank=True, null=True)
    meta_default = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kpi"

    def __str__(self):
        return str(self.nombre)


class KPIResultado(models.Model):
    # Tabla kpi_resultado
    id = models.BigAutoField(primary_key=True)
    kpi = models.ForeignKey(KPI, on_delete=models.PROTECT, related_name="resultados")
    empleado = models.ForeignKey("empleados.Empleado", on_delete=models.CASCADE)
    periodo = models.CharField(max_length=20, help_text=_("Ej: 2025-11"))

    valor = models.DecimalField(max_digits=10, decimal_places=2)
    meta_periodo = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    calculado_automatico = models.BooleanField(default=False)
    observacion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kpi_resultado"
        constraints = [
            models.UniqueConstraint(
                fields=["kpi", "empleado", "periodo"], name="unique_kpi_periodo"
            )
        ]

    def __str__(self):
        return f"{self.kpi} - {self.empleado} ({self.periodo})"
