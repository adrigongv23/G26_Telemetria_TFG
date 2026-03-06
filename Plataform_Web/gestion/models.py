from django.db import models
from django.conf import settings
from temporadas.models import Temporada


class Patrocinio(models.Model):

    TIPO_PATROCINIO = (
        ('economico', 'Económico'),
        ('piezas/materiales', 'Piezas/Materiales'),
        ('mixto', 'Mixto (Dinero y Piezas)'),
    )

    ESTADOS = (
        ('en_contacto', 'En contacto'),
        ('aceptado', 'Aceptado / Activo'),
        ('denegado', 'Denegado'),
    )

    empresa = models.CharField(max_length=100, verbose_name="Nombre de la Empresa")
    persona_contacto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Persona de contacto")
    email_contacto = models.EmailField(verbose_name="Correo de contacto")
    tipo_patrocinio = models.CharField(max_length=30, choices=TIPO_PATROCINIO)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='en_contacto')
    
    # Si el patrocinio es únicamente material, se quedará en 0. Si es económico o mixto, se rellena
    importe_economico = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Importe (€)")

    fecha_contacto = models.DateField(auto_now_add=True)
    # Relaciones
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE, related_name="patrocinios", verbose_name="Temporada del patrocinio")
    contacto_equipo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="patrocinios_gestionados", verbose_name="Persona al cargo del Patrocinio")

    class Meta: 
        verbose_name = "Patrocinio"
        verbose_name_plural = "Patrocinios"

    def __str__(self):
        return f"{self.empresa} ({self.get_estado_display()})"
    
class Pieza(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la pieza/material")
    cantidad = models.PositiveIntegerField(default=1)
    
    # COMPOSICIÓN ESTRICTA: Si se borra el Patrocinio, se borran las Piezas irremediablemente (CASCADE)
    patrocinio = models.ForeignKey(Patrocinio, on_delete=models.CASCADE, related_name="piezas")

    def __str__(self):
        return f"{self.cantidad}x {self.nombre} (De: {self.patrocinio.empresa})"

class Contabilidad(models.Model): 
    concepto = models.CharField(max_length=150)
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    observaciones = models.TextField(blank=True, null=True)
    
    # Relación con Temporada. PROTECT evita que borres una temporada si tiene contabilidad asociada (por temas legales)
    temporada = models.ForeignKey(Temporada, on_delete=models.PROTECT, related_name="%(class)s_registrados")

    class Meta:
        abstract = True  #marcamos la clase como abstracta
        ordering = ['-fecha']
    

class Gasto(Contabilidad):

    CATEGORIAS_GASTOS = (
        ('aerodinamica', 'Aerodinámica'),
        ('chasis', 'Chasis'),
        ('business', 'Business & Operations'),
        ('e_powertrain', 'E-Powertrain'),
        ('electronica', 'Electrónica'),
        ('sdf', 'SDF'),
        ('motor_transmision', 'Motor & Transmisión'),
        ('software', 'Software'),
        ('general', 'General'),
    )
    # Hereda concepto, importe, fecha, observaciones y temporada automáticamente
    categoria = models.CharField(max_length=30, choices=CATEGORIAS_GASTOS, verbose_name="Área del gasto")
    doc_justificativo = models.FileField(upload_to='contabilidad/gastos/', blank=True, null=True, verbose_name="Ticket o Factura (PDF/IMG)")

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"

    def __str__(self):
        return f"[-{self.importe}€] {self.concepto} ({self.temporada})"

class Ingreso(Contabilidad):
    CATEGORIAS_INGRESO = (
        ('patrocinador', 'Patrocinador'),
        ('donación', 'Donación'),
        ('premio', 'Premio'),
        ('recaudación', 'Recaudación'),
        ('Cuotas', 'Cuotas'),
        ('Ventas', 'ventas'),
    )

     # Hereda concepto, importe, fecha, observaciones y temporada automáticamente
    categoria = models.CharField(max_length=30, choices=CATEGORIAS_INGRESO, verbose_name="Categoria del Ingreso")
    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"

    def __str__(self):
        return f"[+{self.importe}€] {self.concepto} ({self.temporada})"
