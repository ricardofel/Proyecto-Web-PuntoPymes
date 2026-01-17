from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

# 1. MOVEMOS EL QUERYSET AL PRINCIPIO
class UsuarioQuerySet(models.QuerySet):
    def para_empresa(self, empresa):
        if empresa is None:
            return self.none()
        return self.filter(empleado__empresa=empresa)

    def busqueda_general(self, texto):
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
        if estado_str == "activo":
            return self.filter(estado=True)
        elif estado_str == "inactivo":
            return self.filter(estado=False)
        return self

    def filtrar_por_rol(self, nombre_rol):
        if not nombre_rol:
            return self
        return self.filter(roles_asignados__nombre=nombre_rol)

    def visibles_para(self, usuario_editor):
        qs = self.exclude(id=usuario_editor.id)
        qs = qs.select_related("empleado", "empleado__empresa").prefetch_related("roles_asignados")

        if usuario_editor.is_superuser:
            return qs # El superuser ve todo (o filtra luego por empresa)
            
        if hasattr(usuario_editor, 'empleado') and usuario_editor.empleado:
            return qs.filter(empleado__empresa=usuario_editor.empleado.empresa)
        
        return qs.none()

# 2. EL MANAGER SE MANTIENE IGUAL
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

# 3. EL MODELO SE CONECTA AQUÍ
class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    # ... (tus campos se mantienen igual: empleado, email, estado, foto, telefono, etc.) ...
    empleado = models.OneToOneField("empleados.Empleado", on_delete=models.CASCADE, related_name="usuario", null=True, blank=True)
    email = models.EmailField(max_length=150, unique=True, verbose_name=_("Correo Electrónico"))
    estado = models.BooleanField(default=True, verbose_name=_("Activo"), help_text=_("TRUE = Puede hacer login"))
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True, verbose_name=_("Foto de Perfil"))
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Teléfono de Contacto"))
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=100, blank=True, null=True)
    ultimo_login = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)

    @property
    def is_active(self):
        return self.estado

    # ... (tus properties es_superadmin_negocio, etc. se mantienen igual) ...
    @property
    def es_superadmin_negocio(self) -> bool:
        return self.roles_asignados.filter(models.Q(nombre__icontains="super") | models.Q(nombre__icontains="gerente"), estado=True).exists()

    @property
    def es_admin_rrhh(self) -> bool:
        return self.roles_asignados.filter(nombre__icontains="rrhh", estado=True).exists()

    @property
    def puede_ver_modulo_usuarios(self) -> bool:
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

    # === ¡LA CORRECCIÓN MÁGICA! ===
    # Esto combina tu Manager con tu QuerySet
    objects = UsuarioManager.from_queryset(UsuarioQuerySet)() 

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "usuario"

    def __str__(self):
        return str(self.email)

# Las clases Rol y UsuarioRol se quedan igual al final
class Rol(models.Model):
    # ... (igual que antes) ...
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    estado = models.BooleanField(default=True)
    usuarios = models.ManyToManyField(Usuario, through="UsuarioRol", related_name="roles_asignados")
    class Meta:
        db_table = "rol"
    def __str__(self):
        return str(self.nombre)

class UsuarioRol(models.Model):
    # ... (igual que antes) ...
    id = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    class Meta:
        db_table = "usuario_rol"
        constraints = [models.UniqueConstraint(fields=["usuario", "rol"], name="unique_usuario_rol")]
    def __str__(self):
        return f"{self.usuario} - {self.rol}"