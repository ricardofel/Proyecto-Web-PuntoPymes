from django.db import models
from django.utils.translation import gettext_lazy as _

"""
Modelos de la app asistencia:

- Turno (Configuración de horarios - Tabla 4)
- EventoAsistencia (Marcaciones GPS/Biométrico - Tabla 24)
- JornadaCalculada (Resumen diario procesado - Tabla 25)

Ver diccionario de datos Tablas 4, 24 y 25.
"""


class Turno(models.Model):
    # Tabla turno
    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey("core.Empresa", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tolerancia_minutos = models.IntegerField(default=0)
    tiempo_comida_minutos = models.IntegerField(default=60)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "turno"

    def __str__(self):
        return f"{self.nombre} ({self.hora_inicio} - {self.hora_fin})"


class EventoAsistencia(models.Model):
    # Tabla evento_asistencia
    class TipoEvento(models.TextChoices):
        CHECK_IN = "check_in", _("Entrada")
        CHECK_OUT = "check_out", _("Salida")
        PAUSA_IN = "pausa_in", _("Inicio Pausa")
        PAUSA_OUT = "pausa_out", _("Fin Pausa")

    id = models.BigAutoField(primary_key=True)
    empleado = models.ForeignKey(
        "empleados.Empleado", on_delete=models.CASCADE, related_name="marcaciones"
    )
    tipo = models.CharField(max_length=20, choices=TipoEvento.choices)
    registrado_el = models.DateTimeField(help_text=_("Fecha hora servidor"))
    latitud = models.DecimalField(
        max_digits=10, decimal_places=8, blank=True, null=True
    )
    longitud = models.DecimalField(
        max_digits=11, decimal_places=8, blank=True, null=True
    )
    precision_gps = models.IntegerField(
        null=True, blank=True, help_text=_("Metros de error")
    )
    foto_url = models.TextField(blank=True, null=True)
    origen = models.CharField(
        max_length=20, blank=True, null=True, help_text=_("app, web, biometrico")
    )
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    observacion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "evento_asistencia"
        indexes = [
            models.Index(fields=["empleado", "registrado_el"]),
        ]


class JornadaCalculada(models.Model):
    # Tabla jornada_calculada
    id = models.BigAutoField(primary_key=True)
    empleado = models.ForeignKey("empleados.Empleado", on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_primera_entrada = models.DateTimeField(null=True, blank=True)
    hora_ultima_salida = models.DateTimeField(null=True, blank=True)
    minutos_trabajados = models.IntegerField(default=0)
    minutos_tardanza = models.IntegerField(default=0)
    minutos_extra = models.IntegerField(default=0)
    estado = models.CharField(
        max_length=20,
        default="incompleto",
        help_text=_("completo, incompleto, ausente"),
    )
    fecha_calculo = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "jornada_calculada"
        constraints = [
            models.UniqueConstraint(
                fields=["empleado", "fecha"], name="unique_jornada_diaria"
            )
        ]
