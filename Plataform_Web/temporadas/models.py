from django.db import models

class Temporada(models.Model):
    # El nombre será algo como "Gades 2024-25"
    nombre = models.CharField(max_length=50, unique=True)
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Presupuesto total para ese año
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Checkbox para marcar cuál es la temporada que estamos viviendo ahora
    actual = models.BooleanField(default=False, verbose_name="¿Es la temporada actual?")

    class Meta:
        # Esto es para que en el panel salga "Temporadas" y no "Temporadas"
        verbose_name = "Temporada"
        verbose_name_plural = "Temporadas"
        ordering = ['-fecha_inicio'] # Ordena las más nuevas primero

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # TRUCO PRO: Si marco esta temporada como "actual", desmarco todas las demás
        # Así evitamos que haya dos temporadas activas a la vez.
        if self.actual:
            Temporada.objects.filter(actual=True).exclude(pk=self.pk).update(actual=False)
        super().save(*args, **kwargs)