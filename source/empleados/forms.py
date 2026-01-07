from django import forms
from .models import Empleado

class EmpleadoForm(forms.ModelForm):
    # Campo "virtual" para manejar los checkboxes
    dias_laborales_select = forms.MultipleChoiceField(
        choices=Empleado.DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-dia'}),
        required=False,
        label="Días Laborales"
    )

    class Meta:
        model = Empleado
        # --- CORRECCIÓN AQUÍ ---
        # En lugar de fields='__all__', usamos exclude.
        # Esto le dice a Django: "Usa todos los campos MENOS dias_laborales"
        exclude = ['dias_laborales']
        # -----------------------
        
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
            'direccion': forms.Textarea(attrs={'rows': 3, 'class': 'resize-none'}),
            'hora_entrada_teorica': forms.TimeInput(attrs={'type': 'time'}),
            'hora_salida_teorica': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Labels vacíos
        self.fields['manager'].empty_label = "Sin manager asignado (Nadie)"
        self.fields['empresa'].empty_label = "Seleccione una Empresa..."
        self.fields['unidad_org'].empty_label = "Seleccione una Unidad..."
        self.fields['puesto'].empty_label = "Seleccione un Puesto..."

        # 1. Cargar datos existentes al editar
        if self.instance.pk and self.instance.dias_laborales:
            self.fields['dias_laborales_select'].initial = self.instance.dias_laborales.split(',')

        # 2. Estilos Tailwind
        for field_name, field in self.fields.items():
            if field_name != 'dias_laborales_select':
                clases = 'block w-full p-2.5 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500'
                if field_name == 'direccion':
                    field.widget.attrs['class'] = clases + ' resize-y'
                    field.widget.attrs['rows'] = 3
                else:
                    field.widget.attrs['class'] = clases

    def save(self, commit=True):
        # Al estar excluido, 'dias_laborales' no se toca en super().save()
        instance = super().save(commit=False)
        
        # Lo llenamos nosotros manualmente aquí:
        lista_dias = self.cleaned_data.get('dias_laborales_select')
        if lista_dias:
            instance.dias_laborales = ",".join(lista_dias)
        else:
            instance.dias_laborales = "" # O un valor por defecto si prefieres
        
        if commit:
            instance.save()
        return instance

    # --- VALIDACIONES (Se mantienen igual) ---
    def clean_nombres(self):
        return self.cleaned_data.get('nombres', '').title()

    def clean_apellidos(self):
        return self.cleaned_data.get('apellidos', '').title()

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if not cedula.isdigit():
            raise forms.ValidationError("La cédula debe contener solo números.")
        if len(cedula) > 10:
             raise forms.ValidationError(f"La cédula no puede tener más de 10 dígitos.")
        
        query = Empleado.objects.filter(cedula=cedula)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            raise forms.ValidationError("Este número de cédula ya está registrado.")
            
        return cedula