# usuarios/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.db import models

from empleados.models import Empleado
from .models import Rol, UsuarioRol
# Importamos el nuevo servicio y las constantes
from usuarios.services.usuario_service import UsuarioService

# Constantes de Estilo (¡Para no repetir CSS!)
STYLE_INPUT_TEXT = (
    "w-full rounded-lg border-slate-300 text-slate-900 shadow-sm "
    "focus:border-blue-500 focus:ring-blue-500 sm:text-sm placeholder-slate-400"
)
STYLE_CHECKBOX = "h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"

User = get_user_model()

class UsuarioForm(forms.ModelForm):
    # Campo "ficticio" para seleccionar roles en la interfaz
    roles = forms.ModelChoiceField(
        queryset=Rol.objects.filter(estado=True),
        widget=forms.RadioSelect(attrs={"class": "form-radio text-blue-600"}),
        required=False,
        label="Asignar Rol",
    )
    
    # Campo para la contraseña (solo escritura)
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
            # Nota: 'nuevo_password' maneja la contraseña, así que no tocamos el campo password del modelo aquí
        }

    def __init__(self, *args, **kwargs):
        # Guardamos quién está editando (request.user) para pasarlo al servicio
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

        # Si estamos editando un usuario existente, marcamos su rol actual en el radio button
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

        return email_normalizado.lower()

    def save(self, commit=True):
        """
        Sobrescribimos save para delegar la lógica compleja al UsuarioService.
        """
        # Obtenemos la instancia del modelo con los datos básicos del form (sin guardar aún en BD)
        usuario = super().save(commit=False)
        
        # Obtenemos todos los datos limpios (incluyendo 'roles' y 'nuevo_password' que no son del modelo)
        data = self.cleaned_data
        
        if commit:
            # ¡Aquí ocurre la magia! Llamamos al servicio
            usuario = UsuarioService.crear_o_actualizar_usuario(
                usuario=usuario,
                data=data,
                editor=self.usuario_actual
            )
            
        return usuario


# ==========================================
# FORMULARIO PARA "MI PERFIL"
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
                    "class": STYLE_INPUT_TEXT.replace("w-full", "w-full p-2.5"), # Ajuste leve
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