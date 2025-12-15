from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _

"""
Modelos de la app usuarios:

- Usuario (Credenciales y MFA - Tabla 7)
- Rol (Catálogo de perfiles - Tabla 8)
- UsuarioRol (Asignación - Tabla 9)

Ver diccionario de datos Tablas 7, 8 y 9.
"""


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("El usuario debe tener un email"))
        email = self.normalize_email(email).strip().lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("estado", True)
        email = self.normalize_email(email).strip().lower()
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    # Tabla usuario
    id = models.BigAutoField(primary_key=True)

    # Relación 1 a 1 con Empleado (FK Ref(empleado))
    # NOTA: Se usa string para evitar import circular
    empleado = models.OneToOneField(
        "empleados.Empleado",
        on_delete=models.CASCADE,
        related_name="usuario",
        null=True,
        blank=True,  # Permitimos null temporalmente para superusers iniciales sin empleado
    )

    email = models.EmailField(
        max_length=150, unique=True, verbose_name=_("Correo Electrónico")
    )

    # Password es manejado internamente por AbstractBaseUser

    estado = models.BooleanField(
        default=True, verbose_name=_("Activo"), help_text=_("TRUE = Puede hacer login")
    )

    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=100, blank=True, null=True)

    # AbstractBaseUser ya tiene last_login, pero el PDF pide ultimo_login explícito.
    # Podemos mapearlo o usar un campo nuevo. Usamos campo nuevo para ser estrictos.
    ultimo_login = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Campos requeridos por Django Admin (no están en PDF pero son necesarios para el framework)
    is_staff = models.BooleanField(default=False)

    # is_active es requerido por Django, lo vinculamos a nuestra propiedad 'estado'
    @property
    def is_active(self):  # type: ignore
        return self.estado

        # --- Helpers de negocio / roles (no generan migraciones) ---

    @property
    def es_superadmin_negocio(self) -> bool:
        """
        True si tiene el rol SUPERADMIN activo en nuestra tabla rol.
        """
        return self.roles_asignados.filter(nombre="Superusuario", estado=True).exists()

    @property
    def es_admin_rrhh(self) -> bool:
        """
        True si tiene el rol ADMIN_RRHH activo.
        """
        return self.roles_asignados.filter(nombre="Admin RRHH", estado=True).exists()

    @property
    def puede_ver_modulo_usuarios(self) -> bool:
        """
        Encapsula toda la lógica de visibilidad del módulo Usuarios.
        Así el template no se llena de condiciones largas.
        """
        return self.is_superuser or self.es_superadmin_negocio or self.es_admin_rrhh

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    @property
    def empresa(self):
        if self.empleado and self.empleado.empresa_id:
            return self.empleado.empresa
        return None

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "usuario"

    def __str__(self):
        return str(self.email)


class Rol(models.Model):
    # Tabla rol
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    estado = models.BooleanField(default=True)

    # Relación M2M inversa para acceso fácil (usuario.roles.all())
    usuarios = models.ManyToManyField(
        Usuario, through="UsuarioRol", related_name="roles_asignados"
    )

    class Meta:
        db_table = "rol"

    def __str__(self):
        return str(self.nombre)


class UsuarioRol(models.Model):
    # Tabla usuario_rol (Pivote)
    id = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        db_table = "usuario_rol"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "rol"], name="unique_usuario_rol"
            )
        ]

    def __str__(self):
        return f"{self.usuario} - {self.rol}"


class UsuarioQuerySet(models.QuerySet):
    def para_empresa(self, empresa):
        if empresa is None:
            return self.none()
        return self.filter(empleado__empresa=empresa)
