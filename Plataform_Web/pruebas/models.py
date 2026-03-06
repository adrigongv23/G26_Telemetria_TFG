from django.db import models
from django.conf import settings
from temporadas.models import Temporada

class Prueba(models.Model):
    CATEGORIAS_TEST = (
        ('aerodinamica', 'Aerodinámica'),
        ('chasis', 'Chasis'),
        ('epowertrain', 'E-Powertrain'),
        ('electronica', 'Electrónica'),
        ('sdf', 'SDF'),
        ('motor_transmision', 'Motor & Transmisión'),
        ('software', 'Software'),
        ('general', 'General'),
    )

    nombre = models.CharField(max_length=150, verbose_name="Nombre del Test")
    descripcion = models.TextField(verbose_name="Objetivo / Descripción de la prueba")
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    categoria = models.CharField(max_length=30, choices=CATEGORIAS_TEST, default='general')
    resultados = models.TextField(blank=True, null=True, verbose_name="Conclusiones y Resultados")
    
    # Relaciones
    # Relacion con Temporada
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE, related_name="pruebas")
    #Relacion con Usuario
    realizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="pruebas_realizadas", verbose_name="Realizado por")

    class Meta:
        verbose_name = "Prueba"
        verbose_name_plural = "Pruebas"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.nombre} ({self.fecha_inicio})"

class Telemetria(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del registro")
    archivo_csv = models.FileField(upload_to='telemetria/archivos_csv/', verbose_name="Archivo de Datos (CSV)")
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    # La telemetría se obtiene durante una Prueba en pista
    prueba = models.ForeignKey(Prueba, on_delete=models.CASCADE, related_name="archivos_telemetria")

    class Meta:
        verbose_name = "Registro de Telemetría"
        verbose_name_plural = "Registros de Telemetría"

    def __str__(self):
        return f"Telemetría: {self.nombre} (De: {self.prueba.nombre})"


class Variable(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre ")
    unidad_medida = models.CharField(max_length=20, verbose_name="Unidad de medida", blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    
    # COMPOSICIÓN 
    telemetria = models.ForeignKey(Telemetria, on_delete=models.CASCADE, related_name="variables")

    class Meta:
        verbose_name = "Variable de Telemetría"
        verbose_name_plural = "Variables de Telemetría"

    def __str__(self):
        unidad = f" [{self.unidad_medida}]" if self.unidad_medida else ""
        return f"{self.nombre}{unidad} (De: {self.telemetria.nombre})"