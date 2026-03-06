from django.contrib import admin
from .models import Prueba, Telemetria, Variable

# INLINES
# Usamos inlines que nos sirve para cuando se este creando un registro de Telemetría, podremos añadir sus Variables en la misma pantalla sin tener que ir a otro menú
class VariableInline(admin.TabularInline):
    model = Variable
    extra = 1 

class TelemetriaInline(admin.TabularInline):
    model = Telemetria
    extra = 0  

# PANELES DE ADMINISTRACIÓN
@admin.register(Prueba)
class PruebaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'fecha_inicio', 'temporada', 'realizado_por')
    
    # Filtros para encontrar los test dado una temporada y una área técnica
    list_filter = ('categoria', 'temporada')
    
    # Buscador de texto
    search_fields = ('nombre', 'descripcion', 'resultados')
    
    # Una barra de navegación en la parte superior, para poder hacer clic en un año y en un mes y mostrar todos los datos de ese me
    date_hierarchy = 'fecha_inicio' 
    
    # Mostramos los archivos de telemetría directamente dentro del test
    inlines = [TelemetriaInline]


@admin.register(Telemetria)
class TelemetriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'prueba', 'fecha_subida')
    
    # Filtra test de telemetría basandose en la temporada o área tecnica de su test correspondiente
    list_filter = ('prueba__temporada', 'prueba__categoria') 
    
    # Buscador del nombre de la telemetría o por el nombre de la prueba
    search_fields = ('nombre', 'prueba__nombre')
    
    # Mostramos las variables de su telemetría
    inlines = [VariableInline]


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    # Aunque se pueden crear desde el Inline, dejamos su tabla propia por si fuese necesario, por prevenir
    list_display = ('nombre', 'unidad_medida', 'telemetria')
    search_fields = ('nombre', 'telemetria__nombre')