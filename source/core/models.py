from django.db import models


class Empresa(models.Model):
    """
    Modelo Empresa.

    Representa la entidad principal para multitenencia.
    Contiene información legal, comercial y de configuración básica.
    """

    id = models.BigAutoField(primary_key=True)

    # Información básica de la empresa
    nombre_comercial = models.CharField(max_length=150)
    razon_social = models.CharField(max_length=255)
    ruc = models.CharField(max_length=20, unique=True)

    # Configuración territorial y monetaria (códigos ISO)
    pais = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text="ISO 3166-1 alpha-2",
    )
    moneda = models.CharField(
        max_length=3,
        blank=True,
        null=True,
        help_text="ISO 4217",
    )

    # Identidad visual y estado
    logo_url = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)

    # Configuración operativa
    zona_horaria = models.CharField(max_length=50)

    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "empresa"

    def __str__(self):
        return str(self.nombre_comercial)


class UnidadOrganizacional(models.Model):
    """
    Modelo UnidadOrganizacional.

    Representa la estructura jerárquica interna de una empresa
    (sucursales, departamentos, filiales, etc.).
    """

    id = models.BigAutoField(primary_key=True)

    # Empresa a la que pertenece la unidad (multitenencia)
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="unidades",
    )

    # Relación jerárquica (unidad padre)
    padre = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hijos",
    )

    # Identificación de la unidad
    nombre = models.CharField(max_length=100)

    # Tipo de unidad organizacional
    tipo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Ej: 'Sucursal', 'Departamento', 'Filial'",
    )

    # Ubicación física o descriptiva
    ubicacion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Dirección física o descripción",
    )

    # Estado lógico de la unidad
    estado = models.BooleanField(default=True)

    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "unidad_organizacional"

    def __str__(self):
        return f"{self.nombre} - {self.empresa}"
