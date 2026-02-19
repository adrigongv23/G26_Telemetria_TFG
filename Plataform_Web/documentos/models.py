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
        ('epowertrain', 'E-Powertrain'),
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
        ('informe', 'Informe Técnico'),
        ('tutorial', 'Tutorial'),
        ('otro', 'Otro'),
    )

    titulo = models.CharField(max_length=100, verbose_name="Título del documento")
    
    # Aquí definimos dónde se guardan los archivos. 
    # upload_to='ingenieria/' creará esa carpeta automáticamente.
    archivo = models.FileField(upload_to='ingenieria_docs/')
    
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    tipo = models.CharField(max_length=20, choices=TIPO_DOC, default='informe')
    
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción o notas")
    
    # RELACIONES (La parte potente)
    # 1. Si borras una temporada, ¿borramos sus documentos? -> models.CASCADE (Sí)
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)
    
    # 2. Si borras un usuario, ¿borramos sus docs? -> models.SET_NULL (No, mejor mantenemos el doc y ponemos usuario a null)
    subido_por = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="documentos_subidos")
    
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento Técnico"
        verbose_name_plural = "Documentos de Ingeniería"
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"{self.titulo} ({self.temporada})"

    def delete(self, *args, **kwargs):
        # Esto borra el archivo físico del disco duro cuando borras la entrada en la base de datos
        if self.archivo:
            if os.path.isfile(self.archivo.path):
                os.remove(self.archivo.path)
        super().delete(*args, **kwargs)