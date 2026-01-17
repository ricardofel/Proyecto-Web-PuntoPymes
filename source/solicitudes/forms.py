from django import forms
from datetime import timedelta
from .models import AprobacionAusencia, SolicitudAusencia, TipoAusencia


class MultipleFileInput(forms.FileInput):
    """
    Widget para permitir selección de múltiples archivos en un solo input.
    """
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        """
        Extrae múltiples archivos del request.FILES cuando el backend lo soporta.
        """
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)


class MultipleFileField(forms.FileField):
    """
    Campo que acepta una lista de archivos en lugar de un solo archivo.
    """

    def to_python(self, data):
        # Retorna la lista sin transformación adicional
        return data

    def clean(self, data, initial=None):
        # Si no es obligatorio y no hay archivos, devuelve None
        if not self.required and not data:
            return None
        # Omite la validación estándar de "un solo archivo"
        return data


class AprobacionForm(forms.ModelForm):
    """
    Formulario para registrar una acción de aprobación con comentario opcional.
    """

    class Meta:
        model = AprobacionAusencia
        fields = ['accion', 'comentario']
        widgets = {
            'accion': forms.Select(attrs={'class': 'form-select block w-full'}),
            'comentario': forms.Textarea(attrs={'class': 'form-textarea block w-full', 'rows': 4}),
        }


class SolicitudAusenciaForm(forms.ModelForm):
    """
    Formulario de solicitud de ausencia.
    Incluye adjuntos múltiples y calcula días hábiles en clean().
    """

    archivos_nuevos = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True, 'class': 'hidden'}),
        label="Adjuntar Documentos"
    )

    class Meta:
        model = SolicitudAusencia
        fields = ['ausencia', 'fecha_inicio', 'fecha_fin', 'motivo']

        ESTILO = "block w-full py-2 px-3 border border-gray-300 rounded-md bg-white shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
        widgets = {
            'ausencia': forms.Select(attrs={'class': ESTILO}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': ESTILO}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': ESTILO}),
            'motivo': forms.Textarea(attrs={'rows': 4, 'class': ESTILO, 'placeholder': 'Describa el motivo...'}),
        }

    def __init__(self, *args, **kwargs):
        # Limita tipos de ausencia a los activos de la empresa del empleado
        empleado = kwargs.pop('empleado', None)
        super().__init__(*args, **kwargs)

        if empleado:
            self.fields['ausencia'].queryset = TipoAusencia.objects.filter(empresa=empleado.empresa, estado=True)

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('fecha_inicio')
        fin = cleaned_data.get('fecha_fin')

        if inicio and fin:
            if fin < inicio:
                self.add_error('fecha_fin', "Fecha fin menor a inicio.")
            else:
                # Calcula días hábiles (lunes=0 ... domingo=6)
                dias = 0
                c = inicio
                while c <= fin:
                    if c.weekday() < 5: dias += 1
                    c += timedelta(days=1)
                self.instance.dias_habiles = int(dias)

        return cleaned_data
