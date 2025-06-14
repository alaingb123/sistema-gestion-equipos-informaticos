from django.db import models
from django.apps import apps

# Create your models here.

class NumeroInventario(models.Model):
    TIPOS_DISPOSITIVOS = [
        ('PC', 'PC'),
        ('Monitor', 'Monitor'),
        ('Teclado', 'Teclado'),
        ('Mouse', 'Mouse'),
        ('Impresora', 'Impresora'),
        ('Scanner', 'Escáner'),
        ('UPS', 'UPS'),
    ]

    codigo = models.CharField(max_length=50)
    tipo_dispositivo = models.CharField(
        max_length=50,
        choices=TIPOS_DISPOSITIVOS,
        blank=True,
        null=True,
        verbose_name='Tipo de Dispositivo'
    )

    def get_dispositivo(self):
        if not self.tipo_dispositivo:
            return None
            
        # Mapeo de tipos de dispositivo a modelos
        tipo_a_modelo = {
            'Monitor': 'Monitor',
            'Teclado': 'Teclado',
            'Mouse': 'Mouse',
            'Impresora': 'Impresora',
            'Scanner': 'Scaner',
            'UPS': 'UPS',
            'PC': 'PC'
        }
        
        if self.tipo_dispositivo in tipo_a_modelo:
            app_label = 'Perifericos' if self.tipo_dispositivo != 'PC' else 'EstacionesTrabajo'
            modelo = apps.get_model(app_label, tipo_a_modelo[self.tipo_dispositivo])
            try:
                return modelo.objects.get(numero_inventario=self)
            except:
                return None
        return None

    def __str__(self):
        partes = [self.codigo]
        if self.tipo_dispositivo:
            partes.append(self.get_tipo_dispositivo_display())  # Usar el método display para mostrar el nombre amigable
        
        dispositivo = self.get_dispositivo()
        if dispositivo and dispositivo.responsable:
            partes.append(f"({dispositivo.responsable})")
            
        return " - ".join(partes)

    class Meta:
        verbose_name = 'Número de Inventario'
        verbose_name_plural = 'Números de Inventario'
        ordering = ['codigo']
        unique_together = ['codigo', 'tipo_dispositivo']

class ComponenteBase(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        abstract = True
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class SistemaOperativo(ComponenteBase):
    class Meta:
        verbose_name = 'Sistema Operativo'
        verbose_name_plural = 'Sistemas Operativos'

class Procesador(ComponenteBase):
    class Meta:
        verbose_name = 'Procesador'
        verbose_name_plural = 'Procesadores'

class RAM(models.Model):
    capacidad = models.CharField(max_length=50)

    def __str__(self):
        return self.capacidad

    class Meta:
        verbose_name = 'Memoria RAM'
        verbose_name_plural = 'Memorias RAM'
        ordering = ['capacidad']

class DiscoDuro(models.Model):
    capacidad = models.CharField(max_length=50)

    def __str__(self):
        return self.capacidad

    class Meta:
        verbose_name = 'Disco Duro'
        verbose_name_plural = 'Discos Duros'
        ordering = ['capacidad']
