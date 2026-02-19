from django.db import models
from users.models import CustomUser
from temporadas.models import Temporada

class Factura(models.Model):
    CATEGORIAS = (
        ('aerodinamica', 'Aerodinámica'),
        ('chasis', 'Chasis'),
        ('business', 'Business & Operations'),
        ('epowertrain', 'E-Powertrain'),
        ('electronica', 'Electrónica'),
        ('sdf', 'SDF'),
        ('motor_transmision', 'Motor & Transmisión'),
        ('software', 'Software'),
        ('general', 'General'),
    )

    nombre = models.CharField(max_length=100, verbose_name="Concepto de la factura")
    empresa = models.CharField(max_length=100, verbose_name="Empresa / Proveedor")
    categoria = models.CharField(max_length=30, choices=CATEGORIAS)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Breve descripción")
    
    # Puede ser foto (jpg/png) o pdf
    archivo = models.FileField(upload_to='facturas/', verbose_name="Foto o PDF de la factura")
    
    # Relaciones
    subido_por = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name="Usuario que la sube")
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} - {self.empresa}"


class Patrocinador(models.Model):

    TIPO_PATROCINIO = (
        ('economico', 'Económico'),
        ('piezas/materiales', 'Piezas/Materiales'),
        ('mixto', 'Mixto (Dinero y Piezas)'),
    )

    ESTADOS = (
        ('en contacto', 'En contacto'),
        ('aceptado', 'Aceptado / Activo'),
        ('denegado', 'Denegado'),
    )

    empresa = models.CharField(max_length=100, verbose_name="Nombre de la Empresa")
    email_contacto = models.EmailField(verbose_name="Correo de contacto")
    tipo_empresa = models.CharField(max_length=30, verbose_name="Tipo de la Empresa")
    tipo_patrocinio = models.CharField(max_length=30, choices=TIPO_PATROCINIO)
    
    # Solo se rellena si el patrocinio es de piezas
    detalle_piezas = models.TextField(blank=True, null=True, help_text="Detallar qué se ofrece si es en especies")
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='contacto')
    
    # Relaciones
    contacto_equipo = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name="Miembro al cargo")
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)

    def __str__(self):
        return self.empresa