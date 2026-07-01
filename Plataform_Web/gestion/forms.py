from django import forms
from .models import Gasto, Ingreso, Patrocinio


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['concepto', 'importe', 'categoria', 'observaciones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ['concepto', 'importe', 'categoria', 'observaciones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PatrocinioForm(forms.ModelForm):
    class Meta:
        model = Patrocinio
        fields = ['empresa', 'email_contacto', 'persona_contacto', 'tipo_patrocinio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PatrocinioEditForm(forms.ModelForm):
    class Meta:
        model = Patrocinio
        fields = ['empresa', 'email_contacto', 'persona_contacto', 'tipo_patrocinio', 'estado', 'importe_economico']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
