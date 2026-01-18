# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Rol, UsuarioRol


class UsuarioRolInline(admin.TabularInline):
    """
    Inline para administrar la relación Usuario–Rol
    directamente desde la vista de detalle del Usuario.

    Usa el modelo intermedio de la relación ManyToMany.
    """

    model = UsuarioRol
    extra = 0  # No muestra filas vacías adicionales por defecto


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Configuración del panel de administración para el modelo Usuario.
    Extiende el UserAdmin base de Django.
    """

    model = Usuario

    # Campos visibles en el listado principal
    list_display = (
        "email",
        "estado",
        "is_staff",
        "is_superuser",
        "ultimo_login",
        "fecha_creacion",
    )

    # Filtros laterales
    list_filter = ("estado", "is_staff", "is_superuser")

    # Campos habilitados para búsqueda
    search_fields = ("email", "empleado__nombres", "empleado__apellidos")

    # Orden por defecto del listado
    ordering = ("email",)

    # Campos de solo lectura en el admin
    readonly_fields = ("last_login", "fecha_creacion")

    # Organización de campos en la vista de edición
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Empleado vinculado", {"fields": ("empleado",)}),
        (
            "Permisos",
            {
                "fields": (
                    "estado",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Fechas importantes",
            {
                "fields": (
                    "last_login",
                    "fecha_creacion",
                )
            },
        ),
    )

    # Campos mostrados al crear un nuevo usuario desde el admin
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "estado",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    # Relación Usuario–Rol editable desde la ficha del usuario
    inlines = [UsuarioRolInline]


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Rol.
    """

    list_display = ("nombre", "estado")
    list_filter = ("estado",)
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    """
    Administración directa del modelo intermedio Usuario–Rol.
    Útil para búsquedas o ajustes puntuales.
    """

    list_display = ("usuario", "rol")
    search_fields = (
        "usuario__email",
        "rol__nombre",
    )
    list_filter = ("rol",)
