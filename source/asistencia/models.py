from django.db import models
from django.utils.translation import gettext_lazy as _

# modelo para la configuración de turnos y horarios
class Turno(models.Model):
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

# registro de eventos de marcación como entradas y salidas
class EventoAsistencia(models.Model):
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

# resumen diario de asistencia para análisis y reportes
class JornadaCalculada(models.Model):
    class EstadoJornada(models.TextChoices):
        PUNTUAL = "puntual", _("Puntual")
        ATRASO = "atraso", _("Atraso")
        FALTA = "falta", _("Falta")
        PERMISO = "permiso", _("Permiso")
        INCOMPLETO = "incompleto", _("Incompleto")
        LIBRE = "libre", _("Día Libre")

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
        choices=EstadoJornada.choices,
        default=EstadoJornada.FALTA,
        help_text=_("Estado calculado para el dashboard"),
    )
    
    fecha_calculo = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "jornada_calculada"
        constraints = [
            models.UniqueConstraint(
                fields=["empleado", "fecha"], name="unique_jornada_diaria"
            )
        ]

    def __str__(self):
        return f"{self.empleado} - {self.fecha} ({self.estado})"

    # método de guardado básico sin lógica automática
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)