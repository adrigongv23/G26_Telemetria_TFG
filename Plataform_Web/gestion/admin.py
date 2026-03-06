from django.contrib import admin
from .models import Patrocinio, Pieza, Gasto, Ingreso

# INLINES 
class PiezaInline(admin.TabularInline):
    model = Pieza
    extra = 1  

# PANEL PARA ADMINISTRACIÓN
@admin.register(Patrocinio)
class PatrocinioAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'estado', 'tipo_patrocinio', 'importe_economico', 'temporada', 'contacto_equipo')
    
    # Para editar el estado y pasar de En contacto a Aceptado o Denagado desde la lista, sin tener que hacerlo manual
    list_editable = ('estado',) 
    
    list_filter = ('estado', 'tipo_patrocinio', 'temporada')
    search_fields = ('empresa', 'persona_contacto', 'email_contacto')
    
    # Metemos las piezas en el patrocinio, por si hiciera falta
    inlines = [PiezaInline]

@admin.register(Pieza)
class PiezaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad', 'patrocinio')
    search_fields = ('nombre', 'patrocinio__empresa')

# CONTABILIDAD (Gastos e Ingresos) 
@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    # Heredamos los campos de Contabilidad
    list_display = ('concepto', 'importe', 'categoria', 'fecha', 'temporada')
    list_filter = ('categoria', 'temporada')
    search_fields = ('concepto', 'observaciones')
    
    # Barra de navegación por fecha de gasto
    date_hierarchy = 'fecha'

@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ('concepto', 'importe', 'categoria', 'fecha', 'temporada')
    list_filter = ('categoria', 'temporada')
    search_fields = ('concepto', 'observaciones')
    
    # Barra de navegación por fecha de ingreso
    date_hierarchy = 'fecha'