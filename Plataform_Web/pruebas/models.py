from django.db import models
from temporadas.models import Temporada

class TestGeneral(models.Model):
    CATEGORIAS_TEST = (
        ('aerodinamica', 'Aerodinámica'),
        ('chasis', 'Chasis'),
        ('business', 'Business & Operations'),
        ('epowertrain', 'E-Powertrain'),
        ('electronica', 'Electrónica'),
        ('sdf', 'SDF'),
        ('motor_transmision', 'Motor & Transmisión'),
        ('general', 'General'),
    )

    nombre = models.CharField(max_length=150, verbose_name="Nombre del Test")
    descripcion = models.TextField(verbose_name="Objetivo / Descripción del test")
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    categoria = models.CharField(max_length=30, choices=CATEGORIAS_TEST, default='general')
    
    resultados = models.TextField(blank=True, null=True, verbose_name="Conclusiones y Resultados")
    
    # Relación
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Test General"
        verbose_name_plural = "Tests Generales"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.nombre} ({self.fecha_inicio})"