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
    nuevo_password = forms.CharField(
    required=False,
    label="Contraseña",
    widget=forms.PasswordInput(
        attrs={
            "class": "w-full rounded-lg border-slate-300 text-slate-900 shadow-sm "
                     "focus:border-blue-500 focus:ring-blue-500 sm:text-sm placeholder-slate-400",
            "placeholder": "••••••••••••",
            "autocomplete": "new-password",
        }
    ),
)


    class Meta:
        model = User
        fields = [
            "email",
            "empleado",
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
                    "placeholder": "••••••••••••",
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
        user = super().save(commit=False)
        raw_password = self.cleaned_data.get("nuevo_password")

        # Si el usuario editado es el mismo que está logueado y cambió contraseña:
        if request.user.pk == user.pk and form.cleaned_data.get("nuevo_password"):
            update_session_auth_hash(request, user)

        if raw_password:
            user.set_password(raw_password)

        if user.pk:
            old_user = User.objects.get(pk=user.pk)
            if "empleado" not in self.data or "empleado" not in self.changed_data:
                user.empleado = old_user.empleado

        if not (self.usuario_actual and self.usuario_actual.is_superuser):
            if user.pk:
                old_user = User.objects.get(pk=user.pk)
                user.is_staff = old_user.is_staff
                user.is_superuser = old_user.is_superuser
            else:
                user.is_staff = False
                user.is_superuser = False

        if commit:
            user.save()
            rol_seleccionado = self.cleaned_data.get("roles")

            if self.usuario_actual and self.usuario_actual.is_superuser:
                UsuarioRol.objects.filter(usuario=user).delete()

                if rol_seleccionado:
                    UsuarioRol.objects.create(usuario=user, rol=rol_seleccionado)
                    if rol_seleccionado.nombre == "Superusuario":
                        user.is_superuser = True
                        user.is_staff = True
                    elif rol_seleccionado.nombre == "Admin RRHH":
                        user.is_superuser = False
                        user.is_staff = True
                    else:
                        user.is_superuser = False
                        user.is_staff = False

                    user.save(update_fields=["is_superuser", "is_staff"])

            empleado = getattr(user, "empleado", None)
            if empleado is not None:
                nuevo_estado = (
                    Empleado.Estado.ACTIVO if user.estado else Empleado.Estado.INACTIVO
                )
                if empleado.estado != nuevo_estado:
                    empleado.estado = nuevo_estado
                    empleado.save(update_fields=["estado"])

        return user


# ==========================================
# NUEVO FORMULARIO PARA "MI PERFIL"
# ==========================================

class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulario limitado para que el usuario gestione sus propios datos
    personales sin afectar roles o estados de cuenta.
    """
    class Meta:
        model = User
        fields = ["foto_perfil", "telefono"]
        widgets = {
            "telefono": forms.TextInput(
                attrs={
                    "class": "w-full rounded-lg border-slate-300 text-slate-900 shadow-sm "
                             "focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2.5",
                    "placeholder": "+593 99 999 9999",
                }
            ),
            "foto_perfil": forms.FileInput(
                attrs={
                    "class": "block w-full text-sm text-slate-500 file:mr-4 file:py-2 "
                             "file:px-4 file:rounded-full file:border-0 file:text-sm "
                             "file:font-semibold file:bg-blue-50 file:text-blue-700 "
                             "hover:file:bg-blue-100 cursor-pointer",
                }
            ),
        }