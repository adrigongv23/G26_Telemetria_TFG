from django.db import models
from users.models import CustomUser
from temporadas.models import Temporada
import os

class Documento(models.Model):
    # Opciones de categorías (puedes añadir más)
    CATEGORIAS = (
        ('aerodinamica', 'Aerodinámica'),
        ('chasis', 'Chasis'),
        ('business', 'Business & Operations'),
        ('e_powertrain', 'E-Powertrain'),
        ('electronica', 'Electrónica'),
        ('sdf', 'SDF'),
        ('motor_transmision', 'Motor & Transmisión'),
        ('software', 'Software'),
        ('normativa', 'General / Normativa'),
    )

    TIPO_DOC = (
        ('fabricacion', 'Fabricación'),
        ('diseno', 'Diseño / CAD'),
        ('concepto', 'Concepto'),
        ('simulacion', 'Simulación'),
        ('dossier_patrocinado', 'Dossier Patrocinio'),
        ('informe', 'Informe'),
        ('tutorial', 'Tutorial'),
        ('otro', 'Otro'),
    )

    # CAMPOS
    nombre = models.CharField(max_length=100, verbose_name="Nombre del documento")
    
    # Aquí definimos dónde se guardan los archivos. 
    # upload_to='ingenieria/' creará esa carpeta automáticamente.
    archivo = models.FileField(upload_to='ingenieria_docs/')
    
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    tipo = models.CharField(max_length=20, choices=TIPO_DOC, default='informe')
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción del documento")
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    # RELACIONES 
    # Relacion Documento - Temporadas (Relación 1..* a 1..* )
    temporada = models.ManyToManyField(Temporada, related_name="documentos_asociados")
    
    # 2. Relación 1 a N con el Usuario (Miembros)
    subido_por = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="documentos_subidos")
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"

    def delete(self, *args, **kwargs):
        # Esto borra el archivo físico del disco duro cuando borras la entrada en la base de datos
        if self.archivo:
            if os.path.isfile(self.archivo.path):
                os.remove(self.archivo.path)
        super().delete(*args, **kwargs)

# Herencia de la clase Factura: Factura hereda de Documento
class Factura(Documento):
    # Al heredar de Documento, ya tiene nombre, archivo, categoria, etc.
    empresa = models.CharField(max_length=100, verbose_name="Nombre de la empresa")
    importe = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Importe (€)")

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"

    def __str__(self):
        return f"Factura {self.empresa} - {self.importe}€"