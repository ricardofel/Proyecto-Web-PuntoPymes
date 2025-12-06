from django import forms
from .models import Empleado

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = '__all__'
        
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
            'direccion': forms.Textarea(attrs={'rows': 3, 'class': 'resize-none'}),
            # El estado ya lo maneja el modelo, no necesitamos widget aquí
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['manager'].empty_label = "Sin manager asignado (Nadie)"
        self.fields['empresa'].empty_label = "Seleccione una Empresa..."
        self.fields['unidad_org'].empty_label = "Seleccione una Unidad..."
        self.fields['puesto'].empty_label = "Seleccione un Puesto..."

        for field_name, field in self.fields.items():
            clases = 'block w-full p-2.5 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500'
            
            if field_name == 'direccion':
                field.widget.attrs['class'] = clases + ' resize-y'
                field.widget.attrs['rows'] = 3
            else:
                field.widget.attrs['class'] = clases

    # --- VALIDACIÓN Y FORMATO DE NOMBRES ---
    def clean_nombres(self):
        nombres = self.cleaned_data.get('nombres')
        if nombres:
            # .title() convierte "juan diego" en "Juan Diego"
            return nombres.title()
        return nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos')
        if apellidos:
            return apellidos.title()
        return apellidos

    # --- VALIDACIÓN DE CÉDULA (Longitud + Duplicados) ---
    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        
        # 1. Validar que sean solo números (opcional pero recomendado)
        if not cedula.isdigit():
            raise forms.ValidationError("La cédula debe contener solo números.")

        # 2. Validar longitud (Máximo 10)
        if len(cedula) > 10:
            raise forms.ValidationError(f"La cédula no puede tener más de 10 dígitos (Ingresaste {len(cedula)}).")
        
        # 3. Validar longitud mínima (Opcional: las cédulas de Ecuador suelen ser 10)
        if len(cedula) < 10:
             raise forms.ValidationError(f"La cédula debe tener 10 dígitos (Ingresaste {len(cedula)}).")

        # 4. Validar Duplicados (Tu lógica existente)
        if self.instance.pk:
            existe = Empleado.objects.filter(cedula=cedula).exclude(pk=self.instance.pk).exists()
        else:
            existe = Empleado.objects.filter(cedula=cedula).exists()
            
        if existe:
            raise forms.ValidationError("¡Atención! Este número de cédula ya está registrado en el sistema.")
            
        return cedula