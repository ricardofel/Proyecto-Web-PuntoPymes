from django import forms
from .models import Empleado, Puesto, Contrato
from core.models import UnidadOrganizacional 

class EmpleadoForm(forms.ModelForm):
    # Campo "virtual" para manejar los checkboxes de días laborales
    dias_laborales_select = forms.MultipleChoiceField(
        choices=Empleado.DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-dia'}),
        required=False,
        label="Días Laborales"
    )

    class Meta:
        model = Empleado
        fields = '__all__'
        exclude = ['dias_laborales', 'foto_url', 'creado_el', 'modificado_el']
        
        widgets = {
            # CORRECCIÓN DE FECHAS Y HORAS (Formatos ISO para HTML5)
            'fecha_nacimiento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'hora_entrada_teorica': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'hora_salida_teorica': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            
            # Textarea estilizado
            'direccion': forms.Textarea(attrs={'rows': 3, 'class': 'resize-none'}),
        }

    def __init__(self, *args, **kwargs):
        # 1. Extraemos el 'empresa_id' que nos manda la vista
        empresa_id = kwargs.pop('empresa_id', None)
        
        super().__init__(*args, **kwargs)
        
        # Labels vacíos para selectores
        self.fields['manager'].empty_label = "Sin manager asignado (Nadie)"
        self.fields['empresa'].empty_label = "Seleccione una Empresa..."
        self.fields['puesto'].empty_label = "Seleccione un Puesto..."
        
        # Ajuste dinámico para unidad (dependiendo de cómo se llame en el modelo)
        campo_unidad = None
        if 'unidad_org' in self.fields:
            self.fields['unidad_org'].empty_label = "Seleccione una Unidad..."
            campo_unidad = 'unidad_org'
        elif 'unidad' in self.fields:
             self.fields['unidad'].empty_label = "Seleccione una Unidad..."
             campo_unidad = 'unidad'
        
        # 2. LOGICA DE FILTRADO POR EMPRESA
        if empresa_id:
            # A. Fijamos la empresa por defecto
            self.fields['empresa'].initial = empresa_id
            
            # B. Filtramos Managers: Solo de esta empresa
            manager_qs = Empleado.objects.filter(
                empresa_id=empresa_id,
                estado='Activo'
            )
            # Excluimos al propio empleado si es edición (para no ser manager de sí mismo)
            if self.instance.pk:
                manager_qs = manager_qs.exclude(pk=self.instance.pk)
            self.fields['manager'].queryset = manager_qs

            # C. Filtramos Unidades: Solo de esta empresa
            if campo_unidad:
                self.fields[campo_unidad].queryset = UnidadOrganizacional.objects.filter(
                    empresa_id=empresa_id
                )

            # D. Filtramos Puestos: Solo de esta empresa
            if 'puesto' in self.fields:
                self.fields['puesto'].queryset = Puesto.objects.filter(
                    empresa_id=empresa_id,
                    estado=True # Solo puestos activos
                ).order_by('nombre')

        # 3. Cargar días laborales (Si es edición)
        if self.instance.pk and self.instance.dias_laborales:
            self.fields['dias_laborales_select'].initial = self.instance.dias_laborales.split(',')

        # 4. Estilos Tailwind Automáticos
        for field_name, field in self.fields.items():
            if field_name != 'dias_laborales_select':
                # Estilo base
                clases = 'block w-full p-2.5 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500'
                
                # Checkboxes especiales (si los hubiera)
                if isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs['class'] = 'w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
                # Textareas (preservamos resize-none si ya lo pusimos en widgets)
                elif isinstance(field.widget, forms.Textarea):
                    existing_class = field.widget.attrs.get('class', '')
                    field.widget.attrs['class'] = f"{clases} {existing_class}"
                # Inputs normales
                else:
                    field.widget.attrs['class'] = clases

    def save(self, commit=True):
        instance = super().save(commit=False)
        lista_dias = self.cleaned_data.get('dias_laborales_select')
        
        if lista_dias:
            instance.dias_laborales = ",".join(lista_dias)
        else:
            instance.dias_laborales = "" 
        
        if commit:
            instance.save()
        return instance

    # --- VALIDACIONES ---
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

# --- FORMULARIO DE CONTRATOS (MANTENIDO) ---
class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        exclude = ['empleado', 'creado_el', 'modificado_el']
        widgets = {
            'fecha_inicio': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'resize-none'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Estilos Tailwind
        for field_name, field in self.fields.items():
            # 1. Checkbox (Estado)
            if field_name == 'estado':
                field.widget.attrs['class'] = 'w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            
            # 2. Input de Archivo (PDF)
            elif field_name == 'archivo_pdf':
                 field.widget.attrs['class'] = 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            
            # 3. Inputs Normales (Texto, Fecha, Número)
            else:
                 clases = 'block w-full p-2.5 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500'
                 
                 # === CORRECCIÓN AQUÍ ===
                 # Si es el salario, le agregamos 'pl-8' (padding-left: 2rem) 
                 # para dejar espacio al icono "$" que pusimos en el HTML.
                 if field_name == 'salario':
                     clases += ' pl-8' 

                 if field_name == 'observaciones':
                     field.widget.attrs['class'] = clases + ' resize-y'
                 else:
                     field.widget.attrs['class'] = clases