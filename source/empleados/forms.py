from django import forms
from django.core.exceptions import ValidationError
from .models import Empleado, Puesto, Contrato
from core.models import UnidadOrganizacional 

class EmpleadoForm(forms.ModelForm):
    """
    formulario principal para la creación y edición de empleados.
    gestiona la validación de datos personales, configuración de jornada
    y filtrado contextual por empresa.
    """
    
    # campo virtual para renderizar los checkboxes de la semana
    dias_laborales_select = forms.MultipleChoiceField(
        choices=Empleado.DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-dia'}),
        required=False,
        label="Días Laborales"
    )

    class Meta:
        model = Empleado
        fields = '__all__'
        # excluimos campos de control interno y el campo de texto plano de días
        exclude = ['dias_laborales', 'foto_url', 'creado_el', 'modificado_el']
        
        widgets = {
            'fecha_nacimiento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'hora_entrada_teorica': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'hora_salida_teorica': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'direccion': forms.Textarea(attrs={'rows': 3, 'class': 'resize-none'}),
        }

    def __init__(self, *args, **kwargs):
        # extracción del objeto empresa enviado desde la vista para evitar el typeerror
        self.empresa_actual = kwargs.pop('empresa_actual', None)
        
        super().__init__(*args, **kwargs)
        
        # configuración de textos por defecto en selectores
        self.fields['manager'].empty_label = "Sin manager asignado (Nadie)"
        self.fields['empresa'].empty_label = "Seleccione una Empresa..."
        self.fields['puesto'].empty_label = "Seleccione un Puesto..."
        
        # detección dinámica del campo de unidad organizacional
        campo_unidad = None
        if 'unidad_org' in self.fields:
            self.fields['unidad_org'].empty_label = "Seleccione una Unidad..."
            campo_unidad = 'unidad_org'
        elif 'unidad' in self.fields:
             self.fields['unidad'].empty_label = "Seleccione una Unidad..."
             campo_unidad = 'unidad'
        
        # lógica de contexto de empresa (si existe empresa preseleccionada)
        if self.empresa_actual:
            empresa_id = self.empresa_actual.id
            
            # 1. fijar valor y ocultar el selector de empresa
            self.fields['empresa'].initial = self.empresa_actual
            self.fields['empresa'].widget = forms.HiddenInput()
            self.fields['empresa'].label = ""
            
            # 2. filtro de managers (excluyendo al propio empleado si es edición)
            manager_qs = Empleado.objects.filter(empresa_id=empresa_id, estado='Activo')
            if self.instance.pk:
                manager_qs = manager_qs.exclude(pk=self.instance.pk)
            self.fields['manager'].queryset = manager_qs

            # 3. filtro de unidades organizacionales
            if campo_unidad:
                self.fields[campo_unidad].queryset = UnidadOrganizacional.objects.filter(
                    empresa_id=empresa_id
                )

            # 4. filtro de puestos activos
            if 'puesto' in self.fields:
                self.fields['puesto'].queryset = Puesto.objects.filter(
                    empresa_id=empresa_id,
                    estado=True
                ).order_by('nombre')

        # carga inicial de días laborales en caso de edición
        if self.instance.pk and self.instance.dias_laborales:
            self.fields['dias_laborales_select'].initial = self.instance.dias_laborales.split(',')

        # inyección de clases tailwind css para estilos unificados
        for field_name, field in self.fields.items():
            # omitimos el campo empresa si está oculto para evitar conflictos visuales
            if field_name == 'empresa' and isinstance(field.widget, forms.HiddenInput):
                continue

            if field_name != 'dias_laborales_select':
                clases = 'block w-full p-2.5 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500'
                
                if isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs['class'] = 'w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
                elif isinstance(field.widget, forms.Textarea):
                    existing_class = field.widget.attrs.get('class', '')
                    field.widget.attrs['class'] = f"{clases} {existing_class}"
                else:
                    field.widget.attrs['class'] = clases

    def save(self, commit=True):
        """
        sobrescritura del método save para procesar la lista de días laborales
        y convertirla en una cadena separada por comas antes de persistir.
        """
        instance = super().save(commit=False)
        lista_dias = self.cleaned_data.get('dias_laborales_select')
        
        if lista_dias:
            instance.dias_laborales = ",".join(lista_dias)
        else:
            instance.dias_laborales = "" 
        
        if commit:
            instance.save()
        return instance

    # --- validaciones personalizadas ---

    def clean_nombres(self):
        return self.cleaned_data.get('nombres', '').title()

    def clean_apellidos(self):
        return self.cleaned_data.get('apellidos', '').title()

    def clean_cedula(self):
        """
        valida que la cédula sea numérica, tenga longitud correcta y sea única
        dentro del contexto (global o por empresa según constraints).
        """
        cedula = self.cleaned_data.get('cedula')
        
        if not cedula.isdigit():
            raise ValidationError("La cédula debe contener solo números.")
        
        if len(cedula) > 10:
             raise ValidationError("La cédula no puede tener más de 10 dígitos.")
        
        # validación de unicidad excluyendo la instancia actual (si es edición)
        query = Empleado.objects.filter(cedula=cedula)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        # validamos unicidad global (ajustar si se requiere unicidad por empresa)
        if query.exists():
            raise ValidationError("Este número de cédula ya está registrado en el sistema.")
            
        return cedula


class ContratoForm(forms.ModelForm):
    """
    formulario para registrar y editar contratos laborales.
    incluye manejo de archivos adjuntos y estilos para moneda.
    """
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
        
        # aplicación de estilos visuales tailwind
        for field_name, field in self.fields.items():
            if field_name == 'estado':
                field.widget.attrs['class'] = 'w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            
            elif field_name == 'archivo_pdf':
                 field.widget.attrs['class'] = 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            
            else:
                 clases = 'block w-full p-2.5 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500'
                 
                 # ajuste visual para campos monetarios
                 if field_name == 'salario':
                     clases += ' pl-8' 

                 if field_name == 'observaciones':
                     field.widget.attrs['class'] = clases + ' resize-y'
                 else:
                     field.widget.attrs['class'] = clases