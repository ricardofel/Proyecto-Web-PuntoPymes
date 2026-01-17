from django import forms
from .models import Objetivo, MetaTactico, Actividad

TAILWIND_INPUT = (
    "w-full rounded-md border border-slate-300 px-3 py-2 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
)


class ObjetivoForm(forms.ModelForm):
    """
    Formulario para crear/editar objetivos del POA.
    """

    class Meta:
        model = Objetivo
        fields = ["nombre", "descripcion", "estado"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": TAILWIND_INPUT, "placeholder": "Nombre del objetivo"}),
            "descripcion": forms.Textarea(attrs={"class": TAILWIND_INPUT, "rows": 3, "placeholder": "Descripción opcional"}),
            "estado": forms.Select(attrs={"class": TAILWIND_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # En creación, inicializa el estado por defecto
        if not self.instance or not getattr(self.instance, "pk", None):
            self.fields["estado"].initial = "activo"


class MetaTacticoForm(forms.ModelForm):
    """
    Formulario para crear/editar metas tácticas del POA.
    """

    class Meta:
        model = MetaTactico
        fields = ["nombre", "descripcion", "indicador", "fecha_inicio", "fecha_fin", "estado"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": TAILWIND_INPUT, "placeholder": "Nombre de la meta"}),
            "descripcion": forms.Textarea(attrs={"class": TAILWIND_INPUT, "rows": 3, "placeholder": "Descripción (opcional)"}),
            "indicador": forms.TextInput(attrs={"class": TAILWIND_INPUT, "placeholder": "Indicador (opcional)"}),
            "fecha_inicio": forms.DateInput(attrs={"class": TAILWIND_INPUT, "type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"class": TAILWIND_INPUT, "type": "date"}),
            "estado": forms.Select(attrs={"class": TAILWIND_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Preformatea fechas para inputs type="date" cuando se edita una instancia existente
        if self.instance and getattr(self.instance, "pk", None):
            if self.instance.fecha_inicio:
                self.initial["fecha_inicio"] = self.instance.fecha_inicio.strftime("%Y-%m-%d")
            if self.instance.fecha_fin:
                self.initial["fecha_fin"] = self.instance.fecha_fin.strftime("%Y-%m-%d")


class ActividadForm(forms.ModelForm):
    """
    Formulario para crear/editar actividades del POA.
    Requiere al menos un ejecutor.
    """

    class Meta:
        model = Actividad
        fields = ["nombre", "descripcion", "fecha_inicio", "fecha_fin", "estado", "ejecutores"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": TAILWIND_INPUT, "placeholder": "Nombre de la actividad"}),
            "descripcion": forms.Textarea(attrs={"class": TAILWIND_INPUT, "rows": 2, "placeholder": "Detalles operativos..."}),
            "fecha_inicio": forms.DateInput(attrs={"class": TAILWIND_INPUT, "type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"class": TAILWIND_INPUT, "type": "date"}),
            "estado": forms.Select(attrs={"class": TAILWIND_INPUT}),
            "ejecutores": forms.SelectMultiple(
                attrs={
                    "class": "w-full rounded-md border border-slate-300 p-2 text-sm focus:ring-2 focus:ring-blue-500",
                    "style": "height: 120px;",
                }
            ),
        }

    def clean_ejecutores(self):
        # Regla de negocio: se exige al menos un ejecutor asignado
        ejecutores = self.cleaned_data.get("ejecutores")
        if not ejecutores or len(ejecutores) == 0:
            raise forms.ValidationError("Debes asignar al menos un ejecutor.")
        return ejecutores

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Preformatea fechas para inputs type="date" cuando se edita una instancia existente
        if self.instance and getattr(self.instance, "pk", None):
            if self.instance.fecha_inicio:
                self.initial["fecha_inicio"] = self.instance.fecha_inicio.strftime("%Y-%m-%d")
            if self.instance.fecha_fin:
                self.initial["fecha_fin"] = self.instance.fecha_fin.strftime("%Y-%m-%d")
