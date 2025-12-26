from django import forms
from .models import Objetivo


class ObjetivoForm(forms.ModelForm):
    class Meta:
        model = Objetivo
        fields = ["nombre", "descripcion", "estado"]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del objetivo",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción opcional",
                }
            ),
            "estado": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }
