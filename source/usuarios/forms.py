from django import forms
from django.contrib.auth import get_user_model
from django.db import models

from empleados.models import Empleado
from .models import Rol, UsuarioRol
from usuarios.services.usuario_service import UsuarioService

# Estilos reutilizables para inputs del formulario
STYLE_INPUT_TEXT = (
    "w-full rounded-lg border-slate-300 text-slate-900 shadow-sm "
    "focus:border-blue-500 focus:ring-blue-500 sm:text-sm placeholder-slate-400"
)
STYLE_CHECKBOX = "h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"

User = get_user_model()

class UsuarioForm(forms.ModelForm):
    # Campo de UI para asignar un rol
    roles = forms.ModelChoiceField(
        queryset=Rol.objects.filter(estado=True),
        widget=forms.RadioSelect(attrs={"class": "form-radio text-blue-600"}),
        required=False,
        label="Asignar Rol",
    )
    
    # Campo virtual para cambio de contraseña
    nuevo_password = forms.CharField(
        required=False,
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": STYLE_INPUT_TEXT,
                "placeholder": "••••••••••••",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        # Campos del modelo que se exponen en este formulario
        fields = [
            "email",
            "empleado",
            "estado", 
        ]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": STYLE_INPUT_TEXT,
                    "placeholder": "ej: usuario@empresa.com",
                }
            ),
            "estado": forms.CheckboxInput(
                attrs={"class": STYLE_CHECKBOX}
            ),
        }

    def __init__(self, *args, **kwargs):
        # Usuario editor (sirve para reglas de permisos dentro del form)
        self.usuario_actual = kwargs.pop("usuario_actual", None)
        super().__init__(*args, **kwargs)

        # Filtra empleados disponibles:
        # - En edición: permite el empleado actual y los no asignados.
        # - En creación: solo los no asignados.
        if self.instance.pk:
            self.fields["empleado"].queryset = Empleado.objects.filter(
                models.Q(usuario__isnull=True) | models.Q(usuario=self.instance)
            )
        else:
            self.fields["empleado"].queryset = Empleado.objects.filter(
                usuario__isnull=True
            )

        # Preselecciona el rol actual (si existe) para edición
        if self.instance.pk:
            rol_actual = Rol.objects.filter(usuariorol__usuario=self.instance).first()
            self.fields["roles"].initial = rol_actual

        # Restricción de edición de roles: solo superuser del sistema
        if not (self.usuario_actual and self.usuario_actual.is_superuser):
            self.fields["roles"].disabled = True

    def clean_email(self):
        # Normaliza email en minúsculas para evitar duplicados 
        # y problemas de consistencia
        email = self.cleaned_data.get("email", "")
        email_normalizado = email.strip()
        if any(c.isupper() for c in email_normalizado):
            raise forms.ValidationError("El correo debe escribirse solo en minúsculas.")
        return email_normalizado.lower()

    def save(self, commit=True):
        # Guarda el modelo y delega la lógica de creación/actualización al servicio
        usuario = super().save(commit=False)
        data = self.cleaned_data
        if commit:
            usuario = UsuarioService.crear_o_actualizar_usuario(
                usuario=usuario,
                data=data,
                editor=self.usuario_actual
            )
        return usuario

class UsuarioEdicionForm(UsuarioForm):
    pass

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["foto_perfil", "telefono"]
        widgets = {
            "telefono": forms.TextInput(
                attrs={
                    "class": STYLE_INPUT_TEXT.replace("w-full", "w-full p-2.5"),
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
