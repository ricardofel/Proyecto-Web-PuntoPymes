from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from django.db.models import Q


class UsuarioQuerySet(models.QuerySet):
    """
    QuerySet con filtros comunes para el modelo Usuario.
    Permite encadenar consultas de forma expresiva.
    """

    def para_empresa(self, empresa):
        # Restringe usuarios a una empresa específica
        if empresa is None:
            return self.none()
        return self.filter(empleado__empresa=empresa)

    def busqueda_general(self, texto):
        # Búsqueda por email y campos del empleado asociado
        if not texto:
            return self
        texto = texto.strip()
        return self.filter(
            Q(email__icontains=texto)
            | Q(empleado__nombres__icontains=texto)
            | Q(empleado__apellidos__icontains=texto)
            | Q(empleado__cedula__icontains=texto)
        )

    def filtrar_por_estado(self, estado_str):
        # Filtra por estado, soportando strings "activo"/"inactivo"
        if estado_str == "activo":
            return self.filter(estado=True)
        elif estado_str == "inactivo":
            return self.filter(estado=False)
        return self

    def filtrar_por_rol(self, nombre_rol):
        # Filtra por nombre de rol asignado
        if not nombre_rol:
            return self
        return self.filter(roles_asignados__nombre=nombre_rol)

    def visibles_para(self, usuario_editor):
        """
        Define qué usuarios son visibles para un usuario editor:
        - Excluye al usuario editor del listado.
        - Superuser: ve todos.
        - Usuario con empleado: ve los usuarios de su misma empresa.
        - Caso contrario: no ve ninguno.
        """
        qs = self.exclude(id=usuario_editor.id)
        qs = qs.select_related("empleado", "empleado__empresa").prefetch_related("roles_asignados")

        if usuario_editor.is_superuser:
            return qs  # Puede verse todo (posibles filtros adicionales se aplican en otro nivel)
            
        if hasattr(usuario_editor, 'empleado') and usuario_editor.empleado:
            return qs.filter(empleado__empresa=usuario_editor.empleado.empresa)
        
        return qs.none()


class UsuarioManager(BaseUserManager):
    """
    Manager del modelo Usuario. Incluye creación de usuario y superusuario.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("El usuario debe tener un email"))
        email = self.normalize_email(email).strip().lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Flags mínimos para administración
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("estado", True)
        email = self.normalize_email(email).strip().lower()
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario principal del sistema basado en email como identificador.
    """

    id = models.BigAutoField(primary_key=True)

    # Datos principales del usuario
    empleado = models.OneToOneField("empleados.Empleado", on_delete=models.CASCADE, related_name="usuario", null=True, blank=True)
    email = models.EmailField(max_length=150, unique=True, verbose_name=_("Correo Electrónico"))
    estado = models.BooleanField(default=True, verbose_name=_("Activo"), help_text=_("TRUE = Puede hacer login"))
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True, verbose_name=_("Foto de Perfil"))
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Teléfono de Contacto"))

    # Campos relacionados a MFA y metadatos de acceso
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=100, blank=True, null=True)
    ultimo_login = models.DateTimeField(null=True, blank=True)

    # Auditoría básica
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Requerido por Django admin (indica si puede acceder al admin)
    is_staff = models.BooleanField(default=False)

    @property
    def is_active(self):
        # Django utiliza is_active en múltiples lugares; aquí se deriva desde "estado"
        return self.estado

    @property
    def es_superadmin_negocio(self) -> bool:
        # Determina si el usuario tiene un rol de negocio con nombre tipo "super" o "gerente"
        return self.roles_asignados.filter(models.Q(nombre__icontains="super") | models.Q(nombre__icontains="gerente"), estado=True).exists()

    @property
    def es_admin_rrhh(self) -> bool:
        # Determina si el usuario tiene un rol de negocio relacionado a RRHH
        return self.roles_asignados.filter(nombre__icontains="rrhh", estado=True).exists()

    @property
    def puede_ver_modulo_usuarios(self) -> bool:
        # Permisos funcionales para el módulo de usuarios
        return self.is_superuser or self.es_superadmin_negocio or self.es_admin_rrhh

    def save(self, *args, **kwargs):
        # Normaliza email antes de persistir
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    @property
    def empresa(self):
        # Acceso directo a la empresa vía el empleado asociado
        if self.empleado and self.empleado.empresa_id:
            return self.empleado.empresa
        return None

    # Manager combinado: permite usar el Manager (create_user, etc.)
    # junto con métodos personalizados del QuerySet (busqueda_general, visibles_para, etc.)
    objects = UsuarioManager.from_queryset(UsuarioQuerySet)() 

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "usuario"

    def __str__(self):
        return str(self.email)


class Rol(models.Model):
    """
    Rol de negocio asignable a usuarios.
    """

    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    estado = models.BooleanField(default=True)

    # Relación ManyToMany con modelo intermedio
    usuarios = models.ManyToManyField(Usuario, through="UsuarioRol", related_name="roles_asignados")

    class Meta:
        db_table = "rol"

    def __str__(self):
        return str(self.nombre)


class UsuarioRol(models.Model):
    """
    Modelo intermedio que representa la asignación de un Rol a un Usuario.
    """

    id = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        db_table = "usuario_rol"
        constraints = [models.UniqueConstraint(fields=["usuario", "rol"], name="unique_usuario_rol")]

    def __str__(self):
        return f"{self.usuario} - {self.rol}"
