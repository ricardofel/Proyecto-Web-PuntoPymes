from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

"""
Modelos de la app POA (Plan Operativo Anual):

- Objetivo (estratégico)
- MetaTactico (táctico) -> tabla 'meta'
- Actividad (operativo)
- Tablas pivote para asignación de responsables/equipos
"""


class Objetivo(models.Model):
    ESTADO_CHOICES = (
        ("activo", "Activo"),
        ("cerrado", "Cerrado"),
        ("archivado", "Archivado"),
    )

    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey("core.Empresa", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    anio = models.IntegerField(help_text=_("Año fiscal (ej: 2025)"))

    # Estado del objetivo (controla ciclo de vida)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="activo")

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    equipo = models.ManyToManyField(
        "empleados.Empleado", through="ObjetivoEmpleado", related_name="objetivos"
    )

    class Meta:
        db_table = "objetivo"

    def __str__(self):
        return f"{self.nombre} ({self.anio})"

    @property
    def avance(self) -> int:
        """
        Avance consolidado del objetivo en porcentaje (0 a 100),
        calculado como: sum(valor_actual) / sum(valor_esperado).
        """
        agg = self.metas_tacticas.aggregate(
            total_esperado=Sum("valor_esperado"),
            total_actual=Sum("valor_actual"),
        )
        total_esperado = agg["total_esperado"] or Decimal("0")
        total_actual = agg["total_actual"] or Decimal("0")

        if total_esperado <= 0:
            return 0

        pct = (total_actual / total_esperado) * Decimal("100")
        pct = max(Decimal("0"), min(Decimal("100"), pct))
        return int(pct)


class ObjetivoEmpleado(models.Model):
    id = models.BigAutoField(primary_key=True)
    objetivo = models.ForeignKey(Objetivo, on_delete=models.CASCADE)
    empleado = models.ForeignKey("empleados.Empleado", on_delete=models.CASCADE)
    rol = models.CharField(
        max_length=50,
        default="lider",
        help_text=_("lider, co-lider, stakeholder"),
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "objetivo_empleado"
        constraints = [
            models.UniqueConstraint(
                fields=["objetivo", "empleado"], name="unique_objetivo_miembro"
            )
        ]

    def __str__(self):
        return f"{self.empleado} en {self.objetivo}"


class MetaTactico(models.Model):
    ESTADO_CHOICES = (
        ("pendiente", "Pendiente"),
        ("en_progreso", "En progreso"),
        ("cumplida", "Cumplida"),
        ("vencida", "Vencida"),
    )

    id = models.BigAutoField(primary_key=True)
    objetivo = models.ForeignKey(
        Objetivo, on_delete=models.CASCADE, related_name="metas_tacticas"
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    indicador = models.CharField(max_length=100, blank=True, null=True)

    valor_esperado = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    valor_actual = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    # Estado de la meta (controla ciclo de vida)
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="pendiente"
    )

    equipo = models.ManyToManyField(
        "empleados.Empleado", through="MetaEmpleado", related_name="metas"
    )

    class Meta:
        db_table = "meta"

    def __str__(self):
        return str(self.nombre)


class MetaEmpleado(models.Model):
    id = models.BigAutoField(primary_key=True)
    meta = models.ForeignKey(MetaTactico, on_delete=models.CASCADE)
    empleado = models.ForeignKey("empleados.Empleado", on_delete=models.CASCADE)
    rol = models.CharField(max_length=50, default="colaborador")

    class Meta:
        db_table = "meta_empleado"
        constraints = [
            models.UniqueConstraint(
                fields=["meta", "empleado"], name="unique_meta_miembro"
            )
        ]


class Actividad(models.Model):
    ESTADO_CHOICES = (
        ("pendiente", "Pendiente"),
        ("en_progreso", "En progreso"),
        ("completada", "Completada"),
        ("cancelada", "Cancelada"),
    )

    id = models.BigAutoField(primary_key=True)
    meta = models.ForeignKey(
        MetaTactico, on_delete=models.CASCADE, related_name="actividades"
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    porcentaje_avance = models.IntegerField(default=0)

    # Estado de la actividad (controla ciclo de vida)
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="pendiente"
    )

    ejecutores = models.ManyToManyField(
        "empleados.Empleado", through="ActividadEmpleado", related_name="actividades"
    )

    class Meta:
        db_table = "actividad"

    def __str__(self):
        return str(self.nombre)


class ActividadEmpleado(models.Model):
    id = models.BigAutoField(primary_key=True)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    empleado = models.ForeignKey("empleados.Empleado", on_delete=models.CASCADE)
    rol = models.CharField(max_length=50, default="ejecutor")

    class Meta:
        db_table = "actividad_empleado"
        constraints = [
            models.UniqueConstraint(
                fields=["actividad", "empleado"], name="unique_actividad_ejecutor"
            )
        ]
