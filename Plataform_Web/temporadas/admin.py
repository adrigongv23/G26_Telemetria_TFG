from django.contrib import admin
from .models import Temporada

@admin.register(Temporada)
class TemporadaAdmin(admin.ModelAdmin):
    # Columnas principales. 
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'presupuesto', 'actual')
    
    # Permite marcar o desmarcar el check de "actual" directamente desde la tabla, sin entrar al detalle
    list_editable = ('actual',)
    
    # Filtro para filtrar por temporadas históricas o actual
    list_filter = ('actual',)
    
    # Buscador de temporadas por nombre
    search_fields = ('nombre',)
    
    # Filtro para ver los miembros de una temporada
    filter_horizontal = ('miembros',)