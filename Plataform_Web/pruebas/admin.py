from django.contrib import admin
from .models import TestGeneral

@admin.register(TestGeneral)
class TestGeneralAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'categoria', 'temporada')
    list_filter = ('categoria', 'temporada')
    search_fields = ('nombre', 'descripcion', 'resultados')