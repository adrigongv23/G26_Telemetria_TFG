from django.contrib import admin
from .models import Temporada

@admin.register(Temporada)
class TemporadaAdmin(admin.ModelAdmin):
    # Esto define qué columnas se ven en la lista
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'presupuesto', 'actual')
    
    # Esto añade un filtro a la derecha para ver rápido cuál es la actual
    list_filter = ('actual',)
    
    # Esto añade una barra de búsqueda por nombre
    search_fields = ('nombre',)