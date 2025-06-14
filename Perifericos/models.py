from django.db import models
from EstacionesTrabajo.models import PC, AreaOrganizativa, Responsable
from ComponentesInternos.models import NumeroInventario

class DispositivoBase(models.Model):
    numero_inventario = models.OneToOneField(
        NumeroInventario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Número de Inventario',
        limit_choices_to=lambda: {'tipo_dispositivo': None},  # Se sobreescribirá en las subclases
        related_name='dispositivo_base'
    )
    pc_asociada = models.ForeignKey(
        PC,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='PC Asociada'
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
        verbose_name='Área',
        null=True,
        blank=True,
    )
    funciona = models.BooleanField(
        default=True,
        verbose_name='¿Funciona?'
    )
    es_proyecto_internacional = models.BooleanField(
        default=False,
        verbose_name='¿Es Proyecto Internacional?'
    )
    marca = models.CharField(
        max_length=100,
        default='Sin especificar',
        verbose_name='Marca'
    )

    class Meta:
        abstract = True

    def clean(self):
        from django.core.exceptions import ValidationError
        # Si hay un número de inventario, verificar que no esté asignado a otro dispositivo
        if self.numero_inventario:
            # Buscar si ya existe un dispositivo con este número de inventario
            model_class = self.__class__
            existing = model_class.objects.filter(
                numero_inventario=self.numero_inventario
            ).exclude(pk=self.pk).first()
            
            if existing:
                # Si el dispositivo existente está asociado a otra PC, no permitir la reasignación
                if existing.pc_asociada and existing.pc_asociada != self.pc_asociada:
                    raise ValidationError(f'Este dispositivo ya está asignado a la PC {existing.pc_asociada}')
                # Si no está asociado a una PC o está asociado a la misma PC, permitir la actualización
                elif not existing.pc_asociada or existing.pc_asociada == self.pc_asociada:
                    existing.delete()  # Eliminar el registro existente para permitir la reasignación

    def save(self, *args, **kwargs):
        # Si hay PC asociada, sincronizar responsable y área
        if self.pc_asociada:
            self.responsable = self.pc_asociada.responsable
            self.area = self.pc_asociada.area
        # Si hay responsable pero no área, sincronizar área
        elif self.responsable and self.responsable.area:
            self.area = self.responsable.area

        # Asignar tipo de dispositivo al número de inventario
        if self.numero_inventario:
            self.numero_inventario.tipo_dispositivo = self.TIPO_DISPOSITIVO
            self.numero_inventario.save()

        super().save(*args, **kwargs)

    def __str__(self):
        partes = []
        if self.numero_inventario:
            partes.append(str(self.numero_inventario))
        if self.responsable:
            print("tiene responsable")
            partes.append(f"de {self.responsable}")
        else:
            print("no tiene responsable")
        if self.area:
            partes.append(f"en {self.area}")
        if partes:
            return " ".join(partes)
        elif self.marca:
            return self.marca
        return "Sin identificación"

class Monitor(DispositivoBase):
    TIPO_DISPOSITIVO = 'Monitor'

    class Meta:
        verbose_name = 'Monitor'
        verbose_name_plural = 'Monitores'

    numero_inventario = models.OneToOneField(
        NumeroInventario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Número de Inventario',
        limit_choices_to={'tipo_dispositivo': 'Monitor'}
    )

class Teclado(DispositivoBase):
    TIPO_DISPOSITIVO = 'Teclado'

    class Meta:
        verbose_name = 'Teclado'
        verbose_name_plural = 'Teclados'

    numero_inventario = models.OneToOneField(
        NumeroInventario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Número de Inventario',
        limit_choices_to={'tipo_dispositivo': 'Teclado'}
    )

class Mouse(DispositivoBase):
    TIPO_DISPOSITIVO = 'Mouse'

    class Meta:
        verbose_name = 'Mouse'
        verbose_name_plural = 'Mouse'

    numero_inventario = models.OneToOneField(
        NumeroInventario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Número de Inventario',
        limit_choices_to={'tipo_dispositivo': 'Mouse'}
    )

class Impresora(DispositivoBase):
    TIPO_DISPOSITIVO = 'Impresora'

    class Meta:
        verbose_name = 'Impresora'
        verbose_name_plural = 'Impresoras'

    numero_inventario = models.OneToOneField(
        NumeroInventario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Número de Inventario',
        limit_choices_to={'tipo_dispositivo': 'Impresora'}
    )

class Scaner(DispositivoBase):
    TIPO_DISPOSITIVO = 'Scanner'

    class Meta:
        verbose_name = 'Escáner'
        verbose_name_plural = 'Escáneres'

    numero_inventario = models.OneToOneField(
        NumeroInventario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Número de Inventario',
        limit_choices_to={'tipo_dispositivo': 'Scanner'}
    )

class UPS(DispositivoBase):
    TIPO_DISPOSITIVO = 'UPS'

    class Meta:
        verbose_name = 'UPS'
        verbose_name_plural = 'UPS'

    numero_inventario = models.OneToOneField(
        NumeroInventario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Número de Inventario',
        limit_choices_to={'tipo_dispositivo': 'UPS'}
    )
