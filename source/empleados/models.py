import os
from django.db import models
from django.utils import timezone 
from django.utils.translation import gettext_lazy as _
from core.storage import private_storage    

"""
Modelos de la app empleados:

- Empleado
- Contrato
- Puesto

Ver diccionario de datos en:
docs/Arquitectura_Estructura_TalentTrack.md
"""

# --- 1. MODELO PUESTO ---
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


# --- UTILIDAD PARA FOTOS ---
def ruta_foto_empleado(instance, filename):
    # instance: es el objeto Empleado.
    # filename: el nombre original del archivo (ej: "foto_playa.jpg").

    # 1. Obtenemos la extensión del archivo original (ej: .jpg, .png)
    ext = filename.split('.')[-1]

    # 2. Creamos un nombre de carpeta único basado en el ID del empleado.
    # Usamos ':08d' para que el ID tenga ceros a la izquierda y se vea profesional.
    folder_name = f"empleado_{instance.id:08d}"

    # 3. Creamos el nombre del archivo (puede ser igual al de la carpeta)
    file_name = f"{folder_name}.{ext}"

    # 4. Construimos la ruta final.
    return os.path.join('empleados', 'fotos', folder_name, file_name)


# --- 2. MODELO EMPLEADO (MODIFICADO) ---
class Empleado(models.Model):
    # Tabla empleado
    
    class Estado(models.TextChoices):
        ACTIVO = "Activo", _("Activo")
        INACTIVO = "Inactivo", _("Inactivo") 
        LICENCIA = "Licencia", _("Licencia")
        SUSPENDIDO = "Suspendido", _("Suspendido")

    # --- DEFINICIÓN DE DÍAS (Para usar en el Formulario) ---
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
    
    # Relaciones
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

    # Datos Personales
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, help_text=_("DNI/Cédula/Pasaporte"))
    email = models.EmailField(
        max_length=150, unique=True, help_text=_("Correo corporativo único")
    )
    
    # Foto
    foto = models.ImageField(upload_to=ruta_foto_empleado, blank=True, null=True)
    
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    
    # Fechas
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_ingreso = models.DateField()
    
    # Estado
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ACTIVO
    )
    
    zona_horaria = models.CharField(max_length=50, blank=True, null=True)

    # --- NUEVOS CAMPOS PARA EL DASHBOARD DE ASISTENCIA ---
    # Estos campos definen el "Deber Ser" para calcular puntualidad (Verde/Naranja)
    hora_entrada_teorica = models.TimeField(default="09:00", help_text="Hora esperada de entrada")
    hora_salida_teorica = models.TimeField(default="18:00", help_text="Hora esperada de salida")
    
    # CAMBIO IMPORTANTE: Este campo guarda los días como TEXTO separado por comas
    # Ejemplo en BD: "LUN,MAR,MIE,JUE,VIE"
    dias_laborales = models.CharField(
        max_length=50, 
        default="LUN,MAR,MIE,JUE,VIE", 
        help_text="Lista de códigos de días laborales separados por comas"
    )
    # -----------------------------------------------------

    class Meta:
        db_table = "empleado"
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "cedula"], name="unique_empresa_cedula"
            )
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    # Lógica de guardado automático (Capitalización)
    def save(self, *args, **kwargs):
        if self.nombres:
            self.nombres = self.nombres.strip().title()
        if self.apellidos:
            self.apellidos = self.apellidos.strip().title()
            
        if self.estado:
            self.estado = self.estado.strip().capitalize()

        super().save(*args, **kwargs)

    # Helper para mostrar nombre completo en templates
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


def ruta_contrato_dinamica(instance, filename):
    # Genera: contratos/empleado_00005/nombre_archivo.pdf
    # El :05d rellena con ceros a la izquierda (1 -> 00001)
    id_empleado = instance.empleado.id
    extension = filename.split('.')[-1]
    
    # Opcional: Si quieres renombrar el archivo también (ej: contrato_2026-01-01.pdf)
    # nombre_limpio = f"contrato_{instance.fecha_inicio}.{extension}"
    # return f'contratos/empleado_{id_empleado:05d}/{nombre_limpio}'
    
    return f'contratos/empleado_{id_empleado:05d}/{filename}'

class Contrato(models.Model):
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
    
    # === CAMBIO AQUÍ: Usamos la función para la ruta ===
    archivo_pdf = models.FileField(
        upload_to=ruta_contrato_dinamica, # <--- Aquí la magia de la carpeta
        storage=private_storage,          # Mantenemos la seguridad
        null=True, blank=True,
        verbose_name="PDF Firmado"
    )
    
    observaciones = models.TextField(blank=True)
    estado = models.BooleanField(default=True, verbose_name="Es contrato vigente")
    
    def __str__(self):
        return f"{self.tipo} - {self.empleado}"