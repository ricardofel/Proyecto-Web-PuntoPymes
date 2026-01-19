from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Empleado, Puesto, Contrato
from core.models import UnidadOrganizacional 

User = get_user_model()

class EmpleadoForm(forms.ModelForm):
    """
    Formulario principal para la gestión de empleados (creación y edición).
    
    Responsabilidades:
    - Validación de datos personales y laborales.
    - Sincronización visual del correo electrónico con el usuario del sistema.
    - Filtrado contextual de claves foráneas (Empresa, Unidad, Puesto, Manager).
    - Transformación de días laborales (lista -> string).
    """

    # Campo explícito para gestionar el email del usuario vinculado
    email = forms.EmailField(
        required=True, 
        label="Correo Electrónico (Usuario de Sistema)"
    )

    # Campo auxiliar para selección múltiple de días laborales
    dias_laborales_select = forms.MultipleChoiceField(
        choices=Empleado.DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-dia'}),
        required=False,
        label="Días Laborales"
    )

    class Meta:
        model = Empleado
        fields = '__all__'
        exclude = ['dias_laborales', 'foto_url', 'creado_el', 'modificado_el', 'usuario']
        
        widgets = {
            'fecha_nacimiento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'fecha_ingreso': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'hora_entrada_teorica': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'hora_salida_teorica': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'direccion': forms.Textarea(attrs={'rows': 3, 'class': 'resize-none'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicialización del formulario con lógica de contexto y precarga de datos.
        """
        self.empresa_actual = kwargs.pop('empresa_actual', None)
        super().__init__(*args, **kwargs)

        # Precarga del email desde el usuario del sistema vinculado
        if self.instance.pk:
            usuario_vinculado = getattr(self.instance, 'usuario', None)
            if usuario_vinculado:
                self.initial['email'] = usuario_vinculado.email

        # Configuración de etiquetas vacías para selectores
        self.fields['manager'].empty_label = "Sin manager asignado (Nadie)"
        self.fields['empresa'].empty_label = "Seleccione una Empresa..."
        self.fields['puesto'].empty_label = "Seleccione un Puesto..."
        
        # Detección y configuración dinámica del campo de unidad organizacional
        campo_unidad = None
        if 'unidad_org' in self.fields:
            self.fields['unidad_org'].empty_label = "Seleccione una Unidad..."
            campo_unidad = 'unidad_org'
        elif 'unidad' in self.fields:
             self.fields['unidad'].empty_label = "Seleccione una Unidad..."
             campo_unidad = 'unidad'
        
        # Filtrado de opciones basado en la empresa del contexto actual
        if self.empresa_actual:
            empresa_id = self.empresa_actual.id
            
            # Configuración del campo empresa (fijar valor y ocultar)
            self.fields['empresa'].initial = self.empresa_actual
            self.fields['empresa'].widget = forms.HiddenInput()
            self.fields['empresa'].label = ""
            
            # Filtrar managers activos de la misma empresa (excluyendo auto-referencia)
            manager_qs = Empleado.objects.filter(empresa_id=empresa_id, estado='Activo')
            if self.instance.pk:
                manager_qs = manager_qs.exclude(pk=self.instance.pk)
            self.fields['manager'].queryset = manager_qs

            # Filtrar unidades y puestos por empresa
            if campo_unidad:
                self.fields[campo_unidad].queryset = UnidadOrganizacional.objects.filter(empresa_id=empresa_id)

            if 'puesto' in self.fields:
                self.fields['puesto'].queryset = Puesto.objects.filter(empresa_id=empresa_id, estado=True).order_by('nombre')

        # Precarga de días laborales seleccionados (string -> list)
        if self.instance.pk and self.instance.dias_laborales:
            self.fields['dias_laborales_select'].initial = self.instance.dias_laborales.split(',')

        # Aplicación de estilos CSS (Tailwind) a los widgets
        self._aplicar_estilos_widgets()

    def _aplicar_estilos_widgets(self):
        """
        Aplica clases de Tailwind CSS a los campos del formulario para mantener consistencia visual.
        """
        for field_name, field in self.fields.items():
            if field_name == 'empresa' and isinstance(field.widget, forms.HiddenInput):
                continue
            
            if field_name != 'dias_laborales_select':
                base_class = 'block w-full p-2.5 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500'
                
                if isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs['class'] = 'w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
                elif isinstance(field.widget, forms.Textarea):
                    existing_class = field.widget.attrs.get('class', '')
                    field.widget.attrs['class'] = f"{base_class} {existing_class}"
                else:
                    field.widget.attrs['class'] = base_class

    def save(self, commit=True):
        """
        Sobrescribe el método save para procesar la selección de días laborales.
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

    def clean_email(self):
        """
        Valida que el correo electrónico sea único en el sistema de usuarios.
        Excluye al usuario actualmente vinculado en caso de edición.
        """
        email = self.cleaned_data.get('email')
        query = User.objects.filter(email=email)
        
        if self.instance.pk:
            usuario_vinculado = getattr(self.instance, 'usuario', None)
            if usuario_vinculado:
                query = query.exclude(pk=usuario_vinculado.pk)
                
        if query.exists():
            raise ValidationError("Este correo electrónico ya está en uso por otro usuario.")
            
        return email

    def clean_nombres(self):
        return self.cleaned_data.get('nombres', '').title()

    def clean_apellidos(self):
        return self.cleaned_data.get('apellidos', '').title()

    def clean_cedula(self):
        """
        Valida formato y unicidad del número de cédula.
        """
        cedula = self.cleaned_data.get('cedula')
        
        if not cedula.isdigit():
            raise ValidationError("La cédula debe contener solo números.")
        
        if len(cedula) > 10:
             raise ValidationError("La cédula no puede tener más de 10 dígitos.")
        
        query = Empleado.objects.filter(cedula=cedula)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
            
        if query.exists():
            raise ValidationError("Este número de cédula ya está registrado en el sistema.")
            
        return cedula


class ContratoForm(forms.ModelForm):
    """
    Formulario para la gestión de contratos laborales asociados a un empleado.
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
        self._aplicar_estilos_widgets()

    def _aplicar_estilos_widgets(self):
        """
        Aplica estilos visuales (Tailwind) específicos para contratos.
        """
        for field_name, field in self.fields.items():
            if field_name == 'estado':
                field.widget.attrs['class'] = 'w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            elif field_name == 'archivo_pdf':
                 field.widget.attrs['class'] = 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            else:
                 base_class = 'block w-full p-2.5 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500'
                 
                 if field_name == 'salario':
                     base_class += ' pl-8' 
                 
                 if field_name == 'observaciones':
                     field.widget.attrs['class'] = base_class + ' resize-y'
                 else:
                     field.widget.attrs['class'] = base_class