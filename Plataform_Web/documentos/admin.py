from django.contrib import admin
from .models import Documento, Factura

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    # Columnas principales 
    list_display = ('nombre', 'categoria', 'tipo', 'subido_por', 'fecha_subida')
    
    # Filtros por área técnica, tipo de documento y temporada del documento
    list_filter = ('categoria', 'tipo', 'temporada')
    
    # Buscador de documentos por su nombre o descripción
    search_fields = ('nombre', 'descripcion')
    
    # Para asignar a que temporada pertenece el documento
    filter_horizontal = ('temporada',)
    
    # Automatización: para rellenar el creador del nuevo documento de manera automática
    def save_model(self, request, obj, form, change):
        if not obj.subido_por:
            obj.subido_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    # Herncia de Documento
    list_display = ('nombre', 'empresa', 'importe', 'categoria', 'subido_por', 'fecha_subida')
    
    list_filter = ('categoria', 'temporada')
    search_fields = ('nombre', 'empresa', 'descripcion')
    
    filter_horizontal = ('temporada',)

    # Mantenemos la misma automatización
    def save_model(self, request, obj, form, change):
        if not obj.subido_por:
            obj.subido_por = request.user
        super().save_model(request, obj, form, change)