from django import forms
from core.models import UnidadOrganizacional
from empleados.models import Puesto
from solicitudes.models import TipoAusencia


class PuestoForm(forms.ModelForm):
    class Meta:
        model = Puesto

        # `empresa` y campos de auditoría se asignan automáticamente (no se editan en el formulario).
        fields = ["nombre", "nivel", "banda_salarial_min", "banda_salarial_max", "descripcion"]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "w-full rounded-lg border-gray-300 text-sm",
                    "placeholder": "Ej: Analista Sr.",
                }
            ),
            "nivel": forms.TextInput(
                attrs={
                    "class": "w-full rounded-lg border-gray-300 text-sm",
                    "placeholder": "Ej: Junior, Senior",
                }
            ),
            "banda_salarial_min": forms.NumberInput(
                attrs={"class": "w-full rounded-lg border-gray-300 text-sm"}
            ),
            "banda_salarial_max": forms.NumberInput(
                attrs={"class": "w-full rounded-lg border-gray-300 text-sm"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "w-full rounded-lg border-gray-300 text-sm",
                    "rows": 2,
                }
            ),
        }


class TipoAusenciaForm(forms.ModelForm):
    class Meta:
        model = TipoAusencia
        fields = ["nombre", "descripcion", "afecta_sueldo", "requiere_documento", "descuenta_vacaciones"]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "w-full rounded-lg border-gray-300 text-sm",
                    "placeholder": "Ej: Vacaciones, Permiso Médico",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "w-full rounded-lg border-gray-300 text-sm",
                    "rows": 2,
                }
            ),
            # Los booleanos usan los widgets por defecto (pueden estilizarse en template si hace falta).
        }


class UnidadOrganizacionalForm(forms.ModelForm):
    # Opciones permitidas para el campo `tipo` (se fuerza el uso de un Select).
    TIPOS_OPCIONES = [
        ("", "--- Seleccione un Tipo ---"),
        ("Empresa", "Empresa"),
        ("Sucursal", "Sucursal"),
        ("Área", "Área"),
        ("Departamento", "Departamento"),
        ("Unidad de negocio", "Unidad de negocio"),
        ("Equipo", "Equipo"),
        ("Oficina", "Oficina"),
    ]

    tipo = forms.ChoiceField(
        choices=TIPOS_OPCIONES,
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm"
            }
        ),
        label="Tipo de Unidad",
    )

    class Meta:
        model = UnidadOrganizacional
        fields = ["padre", "nombre", "tipo", "ubicacion", "estado"]

        # Estilos de widgets (Tailwind).
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm",
                    "placeholder": "Ej: Gerencia Comercial",
                }
            ),
            "ubicacion": forms.TextInput(
                attrs={
                    "class": "w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm",
                    "placeholder": "Ej: Piso 2, Oficina 204",
                }
            ),
            "padre": forms.Select(
                attrs={
                    "class": "w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm"
                }
            ),
            "estado": forms.CheckboxInput(
                attrs={
                    "class": "rounded text-blue-600 focus:ring-blue-500 h-4 w-4"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        # `empresa_id` se usa para restringir el queryset del campo `padre` a la misma empresa.
        empresa_id = kwargs.pop("empresa_id", None)
        super().__init__(*args, **kwargs)

        # Restringir unidades padre a la misma empresa (evita referencias cruzadas entre empresas).
        if empresa_id:
            self.fields["padre"].queryset = UnidadOrganizacional.objects.filter(empresa_id=empresa_id)
            self.fields["padre"].empty_label = "--- Es una Unidad Raíz (Matriz) ---"
