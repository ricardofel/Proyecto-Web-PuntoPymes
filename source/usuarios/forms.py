from django import forms
from django.contrib.auth import get_user_model
from django.db import models

from empleados.models import Empleado
from .models import Rol, UsuarioRol

User = get_user_model()


class UsuarioForm(forms.ModelForm):
    # Campo "ficticio" para seleccionar roles en la interfaz
    roles = forms.ModelChoiceField(
        queryset=Rol.objects.filter(estado=True),
        widget=forms.RadioSelect(attrs={"class": "form-radio text-blue-600"}),
        required=False,
        label="Asignar Rol",
    )

    class Meta:
        model = User  # 👈 IMPORTANTE: aquí está el model del ModelForm
        fields = [
            "email",
            "password",
            "empleado",
            "estado",  # sacamos is_staff, lo controlamos por rol
        ]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full rounded-lg border-slate-300 text-slate-900 shadow-sm "
                    "focus:border-blue-500 focus:ring-blue-500 sm:text-sm placeholder-slate-400",
                    "placeholder": "ej: usuario@empresa.com",
                }
            ),
            "password": forms.PasswordInput(
                attrs={
                    "class": "w-full rounded-lg border-slate-300 text-slate-900 shadow-sm "
                    "focus:border-blue-500 focus:ring-blue-500 sm:text-sm placeholder-slate-400",
                    "placeholder": "••••••••",
                }
            ),
            "estado": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        # quién está editando (request.user)
        self.usuario_actual = kwargs.pop("usuario_actual", None)
        super().__init__(*args, **kwargs)

        # Limitar el combo de empleados
        if self.instance.pk:
            # Editando: empleados sin usuario o el ya asociado
            self.fields["empleado"].queryset = Empleado.objects.filter(
                models.Q(usuario__isnull=True) | models.Q(usuario=self.instance)
            )
        else:
            # Creando: solo empleados que aún NO tienen usuario
            self.fields["empleado"].queryset = Empleado.objects.filter(
                usuario__isnull=True
            )

        # Si estamos editando un usuario existente, marcamos su rol actual
        if self.instance.pk:
            rol_actual = Rol.objects.filter(usuariorol__usuario=self.instance).first()
            self.fields["roles"].initial = rol_actual

        # Si quien edita NO es superuser → no puede cambiar roles
        if not (self.usuario_actual and self.usuario_actual.is_superuser):
            self.fields["roles"].disabled = True

    def clean_email(self):
        email = self.cleaned_data.get("email", "")
        email_normalizado = email.strip()

        # Bloquear si trae mayúsculas
        if any(c.isupper() for c in email_normalizado):
            raise forms.ValidationError(
                "El correo debe escribirse solo en minúsculas (ej: usuario@empresa.com)."
            )

        # Devolvemos en minúsculas por seguridad
        return email_normalizado.lower()

    def save(self, commit=True):
        """
        Guarda el usuario y sincroniza la tabla pivote UsuarioRol.
        Maneja bien el password y respeta jerarquía:
        - Solo superuser puede cambiar roles / is_superuser / is_staff.
        """
        user = super().save(commit=False)
        raw_password = self.cleaned_data.get("password")

        # Manejo de password: si se ingresó uno, lo seteamos; si no, conservamos el anterior
        if raw_password:
            user.set_password(raw_password)
        elif user.pk:
            # No sobreescribir el hash con vacío
            old_user = User.objects.get(pk=user.pk)
            user.password = old_user.password

        # ⚠ Proteger flags si quien edita NO es superuser
        if not (self.usuario_actual and self.usuario_actual.is_superuser):
            if user.pk:
                old_user = User.objects.get(pk=user.pk)
                user.is_staff = old_user.is_staff
                user.is_superuser = old_user.is_superuser
            else:
                # Usuarios creados por RRHH salen como no staff / no superuser
                user.is_staff = False
                user.is_superuser = False

        if commit:
            user.save()

            rol_seleccionado = self.cleaned_data.get("roles")

            # Solo el superuser puede modificar roles y flags críticos
            if self.usuario_actual and self.usuario_actual.is_superuser:
                # Limpiamos relaciones anteriores
                UsuarioRol.objects.filter(usuario=user).delete()

                if rol_seleccionado:
                    # Creamos la relación 1 a 1 en la tabla pivote
                    UsuarioRol.objects.create(usuario=user, rol=rol_seleccionado)

                    # Mapear rol de negocio → flags de Django
                    if rol_seleccionado.nombre == "Superusuario":
                        user.is_superuser = True
                        user.is_staff = True
                    elif rol_seleccionado.nombre == "Admin RRHH":
                        user.is_superuser = False
                        user.is_staff = True
                    else:  # Empleado u otros
                        user.is_superuser = False
                        user.is_staff = False

                    user.save(update_fields=["is_superuser", "is_staff"])

            # --- Sincronizar estado con el Empleado, si existe ---
            empleado = getattr(user, "empleado", None)
            if empleado is not None:
                nuevo_estado = (
                    Empleado.Estado.ACTIVO if user.estado else Empleado.Estado.INACTIVO
                )
                if empleado.estado != nuevo_estado:
                    empleado.estado = nuevo_estado
                    empleado.save(update_fields=["estado"])

        return user
