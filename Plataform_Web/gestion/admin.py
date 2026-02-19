from django.contrib import admin
from .models import Factura, Patrocinador

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'categoria', 'temporada', 'subido_por')
    list_filter = ('categoria', 'temporada')
    search_fields = ('nombre', 'empresa')

@admin.register(Patrocinador)
class PatrocinadorAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'tipo_empresa', 'tipo_patrocinio', 'estado', 'temporada')
    list_filter = ('estado', 'tipo_empresa', 'tipo_patrocinio', 'temporada')
    search_fields = ('empresa', 'email_contacto')