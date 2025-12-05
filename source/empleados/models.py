from django.db import models
from django.utils.translation import gettext_lazy as _

"""
Modelos de la app empleados:

- Empleado
- Contrato
- Puesto

Ver diccionario de datos en:
docs/Arquitectura_Estructura_TalentTrack.md
"""


class Puesto(models.Model):
    # Tabla puesto
    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey(
        "core.Empresa", on_delete=models.CASCADE, related_name="puestos"
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    nivel = models.CharField(
        max_length=50, blank=True, null=True, help_text=_("Ej: Junior, Senior, C-Level")
    )
    banda_salarial_min = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    banda_salarial_max = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "puesto"

    def __str__(self):
        return str(self.nombre)


class Empleado(models.Model):
    # Tabla empleado
    class Estado(models.TextChoices):
        ACTIVO = "activo", _("Activo")
        SUSPENDIDO = "suspendido", _("Suspendido")
        BAJA = "baja", _("Baja")
        LICENCIA = "licencia", _("Licencia")

    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey(
        "core.Empresa", on_delete=models.CASCADE, related_name="empleados"
    )
    unidad_org = models.ForeignKey(
        "core.UnidadOrganizacional", on_delete=models.PROTECT, related_name="empleados"
    )
    puesto = models.ForeignKey(
        Puesto, on_delete=models.PROTECT, related_name="empleados"
    )
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinados",
    )
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, help_text=_("DNI/Cédula/Pasaporte"))
    email = models.EmailField(
        max_length=150, unique=True, help_text=_("Correo corporativo único")
    )
    foto_url = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_ingreso = models.DateField()
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ACTIVO
    )
    zona_horaria = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "empleado"
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "cedula"], name="unique_empresa_cedula"
            )
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class Contrato(models.Model):
    # Tabla contrato
    class Estado(models.TextChoices):
        VIGENTE = "vigente", _("Vigente")
        FINALIZADO = "finalizado", _("Finalizado")
        ANULADO = "anulado", _("Anulado")

    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey("core.Empresa", on_delete=models.CASCADE)
    empleado = models.ForeignKey(
        Empleado, on_delete=models.CASCADE, related_name="contratos"
    )
    turno = models.ForeignKey(
        "asistencia.Turno", on_delete=models.PROTECT, related_name="contratos"
    )
    tipo = models.CharField(max_length=50, help_text=_("Ej: Indefinido, Plazo Fijo"))
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(
        null=True, blank=True, help_text=_("NULL si es Indefinido")
    )
    salario_base = models.DecimalField(max_digits=12, decimal_places=2)
    jornada_semanal_horas = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    documento_url = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.VIGENTE
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "contrato"
        indexes = [
            models.Index(fields=["empleado", "estado"]),
        ]

    def __str__(self):
        return f"Contrato {self.id} - {self.empleado}"
