from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # --- 1. OPCIONES (El Menú) ---
    ROL_CHOICES = (
        ('directiva', 'Directiva'),
        ('jefe_area', 'Jefe de Área'),
        ('empleado', 'Empleado'),
    )

    ESPECIALIDAD_CHOICES = (
        ('aerodinamica', 'Aerodinámica'),
        ('chasis', 'Chasis'),
        ('business', 'Business & Operations'),
        ('epowertrain', 'E-Powertrain'),
        ('electronica', 'Electrónica'),
        ('sdf', 'SDF'),
        ('motor_transmision', 'Motor & Transmisión'),
        ('software', 'Software'),
    )

    # --- 2. CAMPOS (Las Columnas en la BD) ---
    # Usamos la versión con 'verbose_name' porque queda mejor en la web
    rol = models.CharField(
        max_length=20, 
        choices=ROL_CHOICES, 
        default='empleado',
        verbose_name="Rol en el equipo"
    )
    
    especialidad = models.CharField(
        max_length=30, 
        choices=ESPECIALIDAD_CHOICES, 
        null=True, 
        blank=True,
        verbose_name="Área Técnica"
    )

    # --- 3. MÉTODOS ---
    def __str__(self):
        # Muestra: "Nombre Apellido (usuario) - Rol"
        return f"{self.first_name} {self.last_name} ({self.username}) - {self.get_rol_display()}"