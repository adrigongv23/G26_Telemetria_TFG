from django import forms
from .models import Prueba, Telemetria


class PruebaForm(forms.ModelForm):
    class Meta:
        model = Prueba
        fields = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'categoria', 'resultados', 'temporada']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class TelemetriaForm(forms.ModelForm):
    class Meta:
        model = Telemetria
        fields = ['nombre', 'archivo_csv']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'archivo_csv': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
        }
