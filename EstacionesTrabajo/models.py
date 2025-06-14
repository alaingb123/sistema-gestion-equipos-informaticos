from django.db import models
from ComponentesInternos.models import (
    NumeroInventario, SistemaOperativo, Procesador, RAM, DiscoDuro
)

# Create your models here.

class AreaOrganizativa(models.Model):
    nombre = models.CharField(max_length=100)
    area_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Área Principal',
        related_name='departamentos'
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Área Organizativa'
        verbose_name_plural = 'Áreas Organizativas'
        ordering = ['nombre']
        unique_together = ['nombre', 'area_padre']  # Permite nombres repetidos solo si tienen diferente área padre

class Responsable(models.Model):
    nombre = models.CharField(max_length=100)
    area = models.ForeignKey(
        AreaOrganizativa,
        on_delete=models.PROTECT,
        verbose_name='Área',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Responsable'
        verbose_name_plural = 'Responsables'
        ordering = ['nombre']

class PC(models.Model):
    numero_inventario = models.OneToOneField(
        NumeroInventario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Número de Inventario',
        limit_choices_to=models.Q(tipo_dispositivo__isnull=True) | models.Q(tipo_dispositivo='PC')
    )
    responsable = models.ForeignKey(
        Responsable,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Responsable'
    )
    area = models.ForeignKey(
        AreaOrganizativa,
        on_delete=models.PROTECT,
        verbose_name='Área'
    )
    funciona = models.BooleanField(
        default=True,
        verbose_name='¿Funciona?'
    )
    es_proyecto_internacional = models.BooleanField(
        default=False,
        verbose_name='¿Es Proyecto Internacional?'
    )
    sistema_operativo = models.ForeignKey(
        SistemaOperativo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Sistema Operativo'
    )
    procesador = models.ForeignKey(
        Procesador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Procesador'
    )
    ram = models.ForeignKey(
        RAM,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Memoria RAM'
    )
    disco_duro = models.ForeignKey(
        DiscoDuro,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Disco Duro'
    )

    def save(self, *args, **kwargs):
        # Sincronizar área basado en el responsable
        if self.responsable and self.responsable.area:
            self.area = self.responsable.area
        
        # Asignar tipo de dispositivo al número de inventario
        if self.numero_inventario:
            self.numero_inventario.tipo_dispositivo = 'PC'
            self.numero_inventario.save()
            
        super().save(*args, **kwargs)

    def __str__(self):
        if self.numero_inventario:
            return f"PC {self.numero_inventario}"
        elif self.responsable:
            return f"PC de {self.responsable}"
        else:
            return "PC sin identificación"

    class Meta:
        verbose_name = 'Estación de Trabajo'
        verbose_name_plural = 'Estaciones de Trabajo'
        ordering = ['responsable']
