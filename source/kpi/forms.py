from django import forms
from kpi.models import KPI, KPIResultado

class KPIForm(forms.ModelForm):
    class Meta:
        model = KPI
        fields = ['nombre', 'unidad_medida', 'frecuencia', 'meta_default', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 placeholder-slate-400',
                'placeholder': 'Ej: Ventas Mensuales'
            }),
            'unidad_medida': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 placeholder-slate-400',
                'placeholder': 'Ej: %, USD, Unidades'
            }),
            'frecuencia': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-blue-500 bg-white'
            }, choices=[
                ('diaria', 'Diaria'),
                ('semanal', 'Semanal'),
                ('mensual', 'Mensual'),
                ('trimestral', 'Trimestral'),
                ('anual', 'Anual')
            ]),
            'meta_default': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 placeholder-slate-400',
                'rows': 3,
                'placeholder': '¿Qué mide este indicador y por qué es importante?'
            }),
        }
        labels = {
            'meta_default': 'Meta (Objetivo)',
            'unidad_medida': 'Unidad'
        }

class KPIResultadoForm(forms.ModelForm):
        model = KPIResultado
        fields = ['periodo', 'valor', 'observacion']
        widgets = {
             'periodo': forms.TextInput(attrs={
                 'type': 'month', 
                 'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-blue-500 text-slate-600'
             }),
             'valor': forms.NumberInput(attrs={
                 'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-bold text-blue-600 focus:outline-none focus:border-blue-500', 
                 'step': '0.01',
                 'placeholder': '0.00'
             }),
             'observacion': forms.Textarea(attrs={
                 'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-blue-500 placeholder-slate-400', 
                 'rows': 2,
                 'placeholder': 'Notas sobre esta medición...'
             }),
        }