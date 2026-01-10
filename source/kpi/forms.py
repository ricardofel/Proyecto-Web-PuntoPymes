from django import forms
from kpi.models import KPI, KPIResultado

class KPIForm(forms.ModelForm):
    class Meta:
        model = KPI
        fields = ["nombre", "unidad_medida", "frecuencia", "meta_default", "descripcion"]
        
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Ventas Mensuales"}),
            "unidad_medida": forms.TextInput(attrs={"class": "form-control", "placeholder": "%, USD, #..."}),
            "frecuencia": forms.Select(choices=[
                ("mensual", "Mensual"), 
                ("trimestral", "Trimestral"), 
                ("anual", "Anual"),
                ("semanal", "Semanal")
            ], attrs={"class": "form-select"}),
            "meta_default": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

class KPIResultadoForm(forms.ModelForm):
    class Meta:
        model = KPIResultado
        fields = ["periodo", "valor", "observacion"]
        widgets = {
            # Input tipo "month" para seleccionar Enero 2026 fácilmente
            "periodo": forms.TextInput(attrs={"type": "month", "class": "form-control"}),
            "valor": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}),
            "observacion": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Opcional: ¿Por qué este resultado?"}),
        }