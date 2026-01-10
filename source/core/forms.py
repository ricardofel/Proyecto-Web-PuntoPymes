from django import forms
from core.models import UnidadOrganizacional

class UnidadOrganizacionalForm(forms.ModelForm):
    # 1. Definimos las opciones exactas para el menú desplegable
    TIPOS_OPCIONES = [
        ('', '--- Seleccione un Tipo ---'), # Opción vacía por defecto
        ('Empresa', 'Empresa'),
        ('Sucursal', 'Sucursal'),
        ('Área', 'Área'),
        ('Departamento', 'Departamento'),
        ('Unidad de negocio', 'Unidad de negocio'),
        ('Equipo', 'Equipo'),
        ('Oficina', 'Oficina'),
    ]

    # 2. Redefinimos el campo 'tipo' explícitamente para que sea un Select
    tipo = forms.ChoiceField(
        choices=TIPOS_OPCIONES,
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm'
        }),
        label="Tipo de Unidad"
    )

    class Meta:
        model = UnidadOrganizacional
        fields = ['padre', 'nombre', 'tipo', 'ubicacion', 'estado']
        
        # 3. Widgets para el resto de los campos (Estilos Tailwind)
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm', 
                'placeholder': 'Ej: Gerencia Comercial'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm', 
                'placeholder': 'Ej: Piso 2, Oficina 204'
            }),
            'padre': forms.Select(attrs={
                'class': 'w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm'
            }),
            'estado': forms.CheckboxInput(attrs={
                'class': 'rounded text-blue-600 focus:ring-blue-500 h-4 w-4'
            }),
        }

    def __init__(self, *args, **kwargs):
        empresa_id = kwargs.pop('empresa_id', None)
        super().__init__(*args, **kwargs)
        
        # Filtramos para que solo puedas elegir padres de la MISMA empresa
        if empresa_id:
            self.fields['padre'].queryset = UnidadOrganizacional.objects.filter(empresa_id=empresa_id)
            self.fields['padre'].empty_label = "--- Es una Unidad Raíz (Matriz) ---"