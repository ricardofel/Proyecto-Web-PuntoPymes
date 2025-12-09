
# solicitudes/forms.py

from django import forms
from .models import AprobacionAusencia

class AprobacionForm(forms.ModelForm):
    """Formulario usado para crear un registro de aprobación/rechazo de una SolicitudAusencia."""
    class Meta:
        model = AprobacionAusencia
        # Solo necesitamos que el usuario ingrese la acción (aprobar/rechazar) y el comentario.
        # Los campos solicitud y aprobador se llenarán automáticamente en la vista.
        fields = ['accion', 'comentario']

        widgets = {
            # Se usan clases para el estilo, asumiendo que usas algún framework CSS
            'accion': forms.Select(attrs={'class': 'form-select block w-full border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'comentario': forms.Textarea(attrs={'class': 'form-textarea block w-full border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500', 'rows': 4}),
        }