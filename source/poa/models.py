from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _

"""
Modelos de la app poa (Plan Operativo Anual):

- Objetivo (Estratégico)
- MetaTactico (Táctico - Tabla 'meta')
- Actividad (Operativo)
- Tablas pivote de asignación de equipos

Ver diccionario de datos Tablas 18 a 23.
"""


class Objetivo(models.Model):
    # Tabla objetivo (Estratégico)
    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey("core.Empresa", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    anio = models.IntegerField(help_text=_("Año fiscal (ej: 2025)"))
    estado = models.CharField(max_length=20, default="activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Relación ManyToMany a través de tabla intermedia explícita
    equipo = models.ManyToManyField(
        "empleados.Empleado", through="ObjetivoEmpleado", related_name="objetivos"
    )

    class Meta:
        db_table = "objetivo"

    def __str__(self):
        return f"{self.nombre} ({self.anio})"


class ObjetivoEmpleado(models.Model):
    # Tabla objetivo_empleado (Asignación)
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
    # Tabla meta (Táctico)
    # NOTA: Se llama MetaTactico en Python para evitar conflicto con 'class Meta',
    # pero en BD se llamará 'meta' tal como pide el diccionario.
    id = models.BigAutoField(primary_key=True)
    objetivo = models.ForeignKey(
        Objetivo, on_delete=models.CASCADE, related_name="metas_tacticas"
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    indicador = models.CharField(max_length=100, blank=True, null=True)
    valor_esperado = models.DecimalField(max_digits=10, decimal_places=2)
    valor_actual = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0)
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=20, default="pendiente")

    equipo = models.ManyToManyField(
        "empleados.Empleado", through="MetaEmpleado", related_name="metas"
    )

    class Meta:
        db_table = "meta"  # <-- Aquí garantizamos el cumplimiento del PDF

    def __str__(self):
        return str(self.nombre)


class MetaEmpleado(models.Model):
    # Tabla meta_empleado
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
    # Tabla actividad (Operativo)
    id = models.BigAutoField(primary_key=True)
    meta = models.ForeignKey(
        MetaTactico, on_delete=models.CASCADE, related_name="actividades"
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    porcentaje_avance = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, default="pendiente")

    ejecutores = models.ManyToManyField(
        "empleados.Empleado", through="ActividadEmpleado", related_name="actividades"
    )

    class Meta:
        db_table = "actividad"

    def __str__(self):
        return str(self.nombre)


class ActividadEmpleado(models.Model):
    # Tabla actividad_empleado (Ejecutores)
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
