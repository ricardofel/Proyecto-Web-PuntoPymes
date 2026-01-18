from django import forms
from datetime import timedelta
from .models import AprobacionAusencia, SolicitudAusencia, TipoAusencia

# widget para permitir la selección de múltiples archivos en el navegador
class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True
    
    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)

# campo personalizado para procesar listas de archivos sin validación estándar
class MultipleFileField(forms.FileField):
    def to_python(self, data):
        return data

    def clean(self, data, initial=None):
        if not self.required and not data:
            return None
        return data

# formulario para gestionar la aprobación o rechazo de solicitudes
class AprobacionForm(forms.ModelForm):
    class Meta:
        model = AprobacionAusencia
        fields = ['accion', 'comentario']
        widgets = {
            'accion': forms.Select(attrs={'class': 'form-select block w-full'}),
            'comentario': forms.Textarea(attrs={'class': 'form-textarea block w-full', 'rows': 4}),
        }

# formulario principal para la creación y edición de solicitudes
class SolicitudAusenciaForm(forms.ModelForm):
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
                dias = 0
                c = inicio
                while c <= fin:
                    if c.weekday() < 5: dias += 1
                    c += timedelta(days=1)
                self.instance.dias_habiles = int(dias)
        return cleaned_data