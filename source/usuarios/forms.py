# forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Rol, UsuarioRol
from usuarios.models import Usuario

User = get_user_model()


class UsuarioForm(forms.ModelForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Rol.objects.filter(estado=True),
        # Widget para checkboxes con un poco de margen
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-checkbox h-4 w-4 text-blue-600"}
        ),
        required=False,
        label="Asignar Roles",
    )

    class Meta:
        model = Usuario  # O User, según como lo tengas importado
        fields = ["email", "password", "estado"]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full rounded-lg border-slate-300 text-slate-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm placeholder-slate-400",
                    "placeholder": "ej: usuario@empresa.com",
                }
            ),
            "password": forms.PasswordInput(
                attrs={
                    "class": "w-full rounded-lg border-slate-300 text-slate-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm placeholder-slate-400",
                    "placeholder": "••••••••",
                }
            ),
            "estado": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                }
            ),
        }


class UsuarioForm(forms.ModelForm):
    # Campo "ficticio" para seleccionar roles en la interfaz
    roles = forms.ModelMultipleChoiceField(
        queryset=Rol.objects.filter(estado=True),
        widget=forms.CheckboxSelectMultiple,  # O SelectMultiple si prefieres
        required=False,
        label="Asignar Roles",
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "empleado",
            "is_staff",
            "estado",
        ]  # Agrega los que necesites
        widgets = {
            "password": forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando un usuario existente, marcamos sus roles actuales
        if self.instance.pk:
            # Buscamos en la tabla pivote los roles que ya tiene este usuario
            roles_actuales = Rol.objects.filter(usuariorol__usuario=self.instance)
            self.fields["roles"].initial = roles_actuales

    def save(self, commit=True):
        # 1. Guardamos el usuario primero (necesitamos su ID)
        user = super().save(commit=False)

        if commit:
            user.save()
            # Si es creación, necesitamos configurar el password correctamente
            if self.cleaned_data.get("password"):
                user.set_password(self.cleaned_data["password"])
                user.save()

            # 2. Gestión de ROLES (La parte manual)
            roles_seleccionados = self.cleaned_data["roles"]

            # A) Limpiamos roles anteriores (para evitar duplicados o mantener sincronización)
            UsuarioRol.objects.filter(usuario=user).delete()

            # B) Creamos las nuevas relaciones en la tabla pivote
            nuevos_roles = []
            for rol in roles_seleccionados:
                nuevos_roles.append(UsuarioRol(usuario=user, rol=rol))

            # Bulk create es más eficiente que guardar uno por uno
            UsuarioRol.objects.bulk_create(nuevos_roles)

        return user
