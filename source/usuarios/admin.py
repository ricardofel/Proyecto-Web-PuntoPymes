# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Usuario, Rol, UsuarioRol


class UsuarioRolInline(admin.TabularInline):
    """
    Permite gestionar la relación Usuario-Rol desde la ficha del Usuario.
    (Intermediario de la ManyToMany)
    """

    model = UsuarioRol
    extra = 0


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    model = Usuario

    list_display = (
        "email",
        "estado",
        "is_staff",
        "is_superuser",
        "ultimo_login",
        "fecha_creacion",
    )

    list_filter = ("estado", "is_staff", "is_superuser")
    search_fields = ("email", "empleado__nombres", "empleado__apellidos")
    ordering = ("email",)

    readonly_fields = ("last_login", "fecha_creacion")

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

    inlines = [UsuarioRolInline]


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("nombre", "estado")
    list_filter = ("estado",)
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol")
    search_fields = (
        "usuario__email",
        "rol__nombre",
    )
    list_filter = ("rol",)
