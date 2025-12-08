# usuarios/forms.py
from django import forms
from django.contrib.auth import get_user_model
from empleados.models import Empleado
from .models import Rol, UsuarioRol
from django.db import models

User = get_user_model()


class UsuarioForm(forms.ModelForm):
    # Campo "ficticio" para seleccionar roles en la interfaz
    roles = forms.ModelChoiceField(
        queryset=Rol.objects.filter(estado=True),
        widget=forms.RadioSelect(attrs={"class": "form-radio text-blue-600"}),
        required=False,
        label="Asignar Rol",
    )

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

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "empleado",
            "is_staff",
            "estado",
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

    def save(self, commit=True):
        """
        Guarda el usuario y sincroniza la tabla pivote UsuarioRol.
        Maneja bien el password: solo lo cambia si se envía uno nuevo.
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

        if commit:
            user.save()

            rol_seleccionado = self.cleaned_data.get("roles")

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


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full rounded-lg border-slate-300 text-slate-900 shadow-sm "
                "focus:border-blue-500 focus:ring-blue-500 sm:text-sm placeholder-slate-400",
                "placeholder": "ej: usuario@empresa.com",
                "autocomplete": "email",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-lg border-slate-300 text-slate-900 shadow-sm "
                "focus:border-blue-500 focus:ring-blue-500 sm:text-sm placeholder-slate-400",
                "placeholder": "••••••••",
                "autocomplete": "current-password",
            }
        ),
    )
