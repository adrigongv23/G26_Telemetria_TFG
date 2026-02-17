from django.contrib import admin
from .models import Documento

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'tipo', 'temporada', 'subido_por', 'fecha_subida')
    list_filter = ('temporada', 'categoria', 'tipo') # ¡Filtros laterales muy útiles!
    search_fields = ('titulo', 'descripcion')
    
    # Esto hace que el campo "subido_por" se rellene solo con tu usuario al crear un doc
    def save_model(self, request, obj, form, change):
        if not obj.subido_por:
            obj.subido_por = request.user
        super().save_model(request, obj, form, change)