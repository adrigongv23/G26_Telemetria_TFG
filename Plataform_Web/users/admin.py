from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'rol', 'especialidad', 'is_staff')
    
    # Filtramos por rol y área técnica
    list_filter = ('rol', 'especialidad', 'is_staff', 'is_active')
    
    # Buscador de usuarios
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    # Para editar al usuario con los datos insertados
    fieldsets = UserAdmin.fieldsets + (
        ('Información del Equipo Gades', {
            'fields': ('rol', 'especialidad'),
        }),
    )
    
    # Para crear al usuario con los datos insertados
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información del Equipo Gades', {
            'fields': ('rol', 'especialidad'),
        }),
    )