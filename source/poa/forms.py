from django import forms
# ✅ AQUÍ ESTÁ LA CLAVE: Agregamos 'Actividad' a la importación
from .models import Objetivo, MetaTactico, Actividad
from empleados.models import Empleado 
class ObjetivoForm(forms.ModelForm):
    class Meta:
        model = Objetivo
        fields = ["nombre", "descripcion", "estado"]

        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del objetivo"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción opcional",
                }
            ),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance or not getattr(self.instance, "pk", None):
            self.fields["estado"].initial = "activo"


class MetaTacticoForm(forms.ModelForm):
    class Meta:
        model = MetaTactico
        fields = [
            "nombre",
            "descripcion",
            "indicador",
            "valor_esperado",
            "valor_actual",
            "fecha_inicio",
            "fecha_fin",
            "estado",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre de la meta"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción (opcional)",
                }
            ),
            "indicador": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Indicador (opcional)"}
            ),
            "valor_esperado": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}
            ),
            "valor_actual": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}
            ),
            "fecha_inicio": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = [
            "nombre",
            "descripcion",
            "fecha_inicio",
            "fecha_fin",
            "estado",
            "ejecutores",
        ]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre de la actividad"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Detalles operativos...",
                }
            ),
            "fecha_inicio": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }