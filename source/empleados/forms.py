from django import forms
from .models import Empleado

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        # Aquí definimos qué campos queremos en el formulario
        fields = [
            'empresa', 'unidad_org', 'puesto', 'nombres', 'apellidos',
            'cedula', 'email', 'telefono', 'fecha_ingreso', 'zona_horaria'
        ]
        
        # Esto es magia: Le inyectamos clases CSS a los inputs de Django
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'apellidos': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'cedula': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'telefono': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded-lg'}),
            'empresa': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg bg-white'}),
            'unidad_org': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg bg-white'}),
            'puesto': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg bg-white'}),
            'zona_horaria': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
        }