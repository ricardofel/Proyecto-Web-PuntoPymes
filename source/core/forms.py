from django import forms
from core.models import UnidadOrganizacional

class UnidadOrganizacionalForm(forms.ModelForm):
    class Meta:
        model = UnidadOrganizacional
        # Ocultamos 'empresa' porque la asignaremos automáticamente según la selección
        fields = ['padre', 'nombre', 'tipo', 'ubicacion', 'estado']
        widgets = {
            'padre': forms.Select(attrs={'class': 'w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm'}),
            'nombre': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm', 'placeholder': 'Ej: Gerencia de Finanzas'}),
            'tipo': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm', 'placeholder': 'Ej: Departamento, Sucursal'}),
            'ubicacion': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm', 'placeholder': 'Ej: Edificio Norte, Piso 2'}),
            'estado': forms.CheckboxInput(attrs={'class': 'rounded text-blue-600 focus:ring-blue-500 h-4 w-4'}),
        }

    def __init__(self, *args, **kwargs):
        # Recibimos el ID de la empresa para filtrar el campo 'padre'
        empresa_id = kwargs.pop('empresa_id', None)
        super().__init__(*args, **kwargs)
        
        if empresa_id:
            # Solo mostramos unidades de la MISMA empresa como opciones para ser "Padre"
            self.fields['padre'].queryset = UnidadOrganizacional.objects.filter(empresa_id=empresa_id)
            self.fields['padre'].empty_label = "--- Es una Unidad Raíz (Matriz) ---"