from django.db import models
from django.utils.translation import gettext_lazy as _


class Empresa(models.Model):
    # Tabla empresa
    id = models.BigAutoField(primary_key=True)
    nombre_comercial = models.CharField(max_length=150)
    razon_social = models.CharField(max_length=255)
    ruc = models.CharField(max_length=20, unique=True)
    pais = models.CharField(
        max_length=2, blank=True, null=True, help_text="ISO 3166-1 alpha-2"
    )
    moneda = models.CharField(max_length=3, blank=True, null=True, help_text="ISO 4217")
    logo_url = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)
    zona_horaria = models.CharField(max_length=50)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "empresa"

    def __str__(self):
        return str(self.nombre_comercial)


class UnidadOrganizacional(models.Model):
    # Tabla unidad_organizacional
    id = models.BigAutoField(primary_key=True)

    # FK1: empresa_id [FK, NOT NULL]
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="unidades"
    )

    # FK2: padre_id [FK, NULL]
    padre = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="hijos"
    )

    # nombre: VARCHAR(100) [NOT NULL]
    nombre = models.CharField(max_length=100)

    # tipo: VARCHAR(50) -- Coincidencia exacta con el diagrama (help_text agregado)
    tipo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Ej: 'Sucursal', 'Departamento', 'Filial'",
    )

    # ubicacion: VARCHAR(255) -- Coincidencia exacta con el diagrama
    ubicacion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Dirección física o descripción",
    )

    # estado: BOOLEAN [DEFAULT TRUE]
    estado = models.BooleanField(default=True)

    # fecha_creacion: TIMESTAMPTZ [DEFAULT NOW()]
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "unidad_organizacional"

    def __str__(self):
        return f"{self.nombre} - {self.empresa}"
