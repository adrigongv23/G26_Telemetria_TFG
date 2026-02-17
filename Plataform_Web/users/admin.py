from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # Esto añade una sección nueva al editar un usuario existente
    fieldsets = UserAdmin.fieldsets + (
        ('Información del Equipo (TFG)', {'fields': ('rol', 'especialidad')}),
    )
    
    # Esto permite añadir estos campos cuando creas un usuario nuevo desde el admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información del Equipo (TFG)', {'fields': ('rol', 'especialidad')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)