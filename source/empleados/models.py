import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.storage import private_storage

# --- utilidades de sistema de archivos ---

def ruta_foto_empleado(instance, filename):
    """
    genera una ruta única para la foto de perfil basada en el id del empleado.
    estructura: empleados/fotos/empleado_0000000X/archivo.ext
    """
    ext = filename.split('.')[-1]
    folder_name = f"empleado_{instance.id:08d}"
    file_name = f"{folder_name}.{ext}"
    return os.path.join('empleados', 'fotos', folder_name, file_name)


def ruta_contrato_dinamica(instance, filename):
    """
    genera una ruta organizada por carpetas de empleado para los contratos.
    estructura: contratos/empleado_0000X/archivo.pdf
    """
    id_empleado = instance.empleado.id
    return f'contratos/empleado_{id_empleado:05d}/{filename}'


# --- modelos de datos ---

class Puesto(models.Model):
    """
    representa un cargo o posición laboral dentro de la estructura empresarial.
    define las bandas salariales y el nivel jerárquico asociado.
    """
    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey(
        "core.Empresa", on_delete=models.CASCADE, related_name="puestos"
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    nivel = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text=_("Ej: Junior, Senior, C-Level")
    )
    
    # rango salarial referencial para el puesto
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
    """
    entidad central que gestiona la información personal, laboral y de configuración
    de asistencia del colaborador.
    """
    
    class Estado(models.TextChoices):
        ACTIVO = "Activo", _("Activo")
        INACTIVO = "Inactivo", _("Inactivo") 
        LICENCIA = "Licencia", _("Licencia")
        SUSPENDIDO = "Suspendido", _("Suspendido")

    # constantes para mapeo de días laborales
    DIAS_SEMANA = [
        ('LUN', 'Lunes'),
        ('MAR', 'Martes'),
        ('MIE', 'Miércoles'),
        ('JUE', 'Jueves'),
        ('VIE', 'Viernes'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
    ]

    id = models.BigAutoField(primary_key=True)
    
    # relaciones organizacionales
    empresa = models.ForeignKey(
        "core.Empresa", on_delete=models.CASCADE, related_name="empleados"
    )
    unidad_org = models.ForeignKey(
        "core.UnidadOrganizacional", on_delete=models.PROTECT, related_name="empleados"
    )
    puesto = models.ForeignKey(
        "Puesto", on_delete=models.PROTECT, related_name="empleados"
    )
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinados",
    )

    # información personal e identificación
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, help_text=_("DNI/Cédula/Pasaporte"))
    email = models.EmailField(
        max_length=150, unique=True, help_text=_("Correo corporativo único")
    )
    
    foto = models.ImageField(upload_to=ruta_foto_empleado, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    
    # fechas relevantes
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_ingreso = models.DateField()
    
    # estado y configuración regional
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ACTIVO
    )
    zona_horaria = models.CharField(max_length=50, blank=True, null=True)

    # configuración de asistencia y puntualidad
    hora_entrada_teorica = models.TimeField(default="09:00", help_text="Hora esperada de entrada")
    hora_salida_teorica = models.TimeField(default="18:00", help_text="Hora esperada de salida")
    
    # almacenamiento de días laborales como cadena csv (ej: "LUN,MAR,MIE")
    # esto facilita la persistencia simple sin tablas intermedias complejas.
    dias_laborales = models.CharField(
        max_length=50, 
        default="LUN,MAR,MIE,JUE,VIE", 
        help_text="Lista de códigos de días laborales separados por comas"
    )

    class Meta:
        db_table = "empleado"
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "cedula"], name="unique_empresa_cedula"
            )
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    def save(self, *args, **kwargs):
        """
        normalización de datos antes de persistir en base de datos.
        aplica formato título a nombres/apellidos y capitalización al estado.
        """
        if self.nombres:
            self.nombres = self.nombres.strip().title()
        if self.apellidos:
            self.apellidos = self.apellidos.strip().title()
            
        if self.estado:
            self.estado = self.estado.strip().capitalize()

        super().save(*args, **kwargs)

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


class Contrato(models.Model):
    """
    historial de vinculaciones contractuales del empleado.
    permite almacenar el documento firmado en un almacenamiento seguro (fuera de /media público).
    """
    TIPOS = [
        ('Indefinido', 'Tiempo Indefinido'),
        ('Plazo Fijo', 'Plazo Fijo'),
        ('Obra', 'Por Obra o Servicio'),
        ('Eventual', 'Eventual / Pasantía'),
    ]

    empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE, related_name='contratos')
    tipo = models.CharField(max_length=50, choices=TIPOS)
    
    cargo_en_contrato = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    
    # archivo protegido mediante private_storage para evitar acceso público no autorizado
    archivo_pdf = models.FileField(
        upload_to=ruta_contrato_dinamica,
        storage=private_storage,
        null=True, blank=True,
        verbose_name="PDF Firmado"
    )
    
    observaciones = models.TextField(blank=True)
    estado = models.BooleanField(default=True, verbose_name="Es contrato vigente")
    
    def __str__(self):
        return f"{self.tipo} - {self.empleado}"