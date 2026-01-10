from django import forms
from .models import Objetivo, MetaTactico, Actividad
from empleados.models import Empleado 

# Definimos un estilo común de Tailwind para no repetir código
TAILWIND_INPUT = "w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"

class ObjetivoForm(forms.ModelForm):
    class Meta:
        model = Objetivo
        fields = ["nombre", "descripcion", "estado"]

        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": TAILWIND_INPUT, "placeholder": "Nombre del objetivo"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": TAILWIND_INPUT,
                    "rows": 3,
                    "placeholder": "Descripción opcional",
                }
            ),
            "estado": forms.Select(attrs={"class": TAILWIND_INPUT}),
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
                attrs={"class": TAILWIND_INPUT, "placeholder": "Nombre de la meta"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": TAILWIND_INPUT,
                    "rows": 3,
                    "placeholder": "Descripción (opcional)",
                }
            ),
            "indicador": forms.TextInput(
                attrs={"class": TAILWIND_INPUT, "placeholder": "Indicador (opcional)"}
            ),
            "valor_esperado": forms.NumberInput(
                attrs={"class": TAILWIND_INPUT, "step": "0.01", "placeholder": "0.00"}
            ),
            "valor_actual": forms.NumberInput(
                attrs={"class": TAILWIND_INPUT, "step": "0.01", "placeholder": "0.00"}
            ),
            "fecha_inicio": forms.DateInput(
                attrs={"class": TAILWIND_INPUT, "type": "date"}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"class": TAILWIND_INPUT, "type": "date"}
            ),
            "estado": forms.Select(attrs={"class": TAILWIND_INPUT}),
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
                attrs={"class": TAILWIND_INPUT, "placeholder": "Nombre de la actividad"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": TAILWIND_INPUT,
                    "rows": 2,
                    "placeholder": "Detalles operativos...",
                }
            ),
            "fecha_inicio": forms.DateInput(
                attrs={"class": TAILWIND_INPUT, "type": "date"}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"class": TAILWIND_INPUT, "type": "date"}
            ),
            "estado": forms.Select(attrs={"class": TAILWIND_INPUT}),
            
            # 👇 AQUÍ ESTÁ EL ARREGLO FINAL
            "ejecutores": forms.SelectMultiple(
                attrs={
                    # Usamos 'w-full' para que ocupe todo el ancho y no se salga
                    "class": "w-full rounded-md border border-slate-300 p-2 text-sm focus:ring-2 focus:ring-blue-500", 
                    "style": "height: 120px;", # Altura fija para que se vea ordenado
                }
            ),
        }