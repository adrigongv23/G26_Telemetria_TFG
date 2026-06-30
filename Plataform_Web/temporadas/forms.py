from django import forms
from .models import Temporada


class TemporadaForm(forms.ModelForm):
    class Meta:
        model = Temporada
        fields = ['nombre', 'fecha_inicio', 'fecha_fin', 'presupuesto', 'actual', 'miembros']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'miembros': forms.CheckboxSelectMultiple(),
        }
