from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, BooleanWidget
from .models import Monitor, Teclado, Mouse, Impresora, Scaner, UPS
from EstacionesTrabajo.models import PC, AreaOrganizativa, Responsable
from ComponentesInternos.models import NumeroInventario

class SiNoWidget(BooleanWidget):
    def render(self, value, obj=None, **kwargs):
        return 'SI' if value else 'NO'

class BasePerifericoResource(resources.ModelResource):
    numero_inventario = fields.Field(
        column_name='No. Inv.',
        attribute='numero_inventario',
        widget=ForeignKeyWidget(NumeroInventario, 'codigo')
    )
    responsable = fields.Field(
        column_name='Responsable',
        attribute='responsable',
        widget=ForeignKeyWidget(Responsable, 'nombre')
    )
    area = fields.Field(
        column_name='Área',
        attribute='area',
        widget=ForeignKeyWidget(AreaOrganizativa, 'nombre')
    )
    pc_asociada = fields.Field(
        column_name='PC Asociada',
        attribute='pc_asociada',
        widget=ForeignKeyWidget(PC, 'numero_inventario')
    )
    funciona = fields.Field(
        column_name='Estado',
        attribute='funciona',
        widget=SiNoWidget()
    )
    es_proyecto_internacional = fields.Field(
        column_name='Proyecto Int.',
        attribute='es_proyecto_internacional',
        widget=SiNoWidget()
    )

    class Meta:
        abstract = True
        fields = ('numero_inventario', 'responsable', 'area', 'pc_asociada', 
                 'funciona', 'es_proyecto_internacional', 'marca')
        export_order = fields

class MonitorResource(BasePerifericoResource):
    class Meta(BasePerifericoResource.Meta):
        model = Monitor

class TecladoResource(BasePerifericoResource):
    class Meta(BasePerifericoResource.Meta):
        model = Teclado

class MouseResource(BasePerifericoResource):
    class Meta(BasePerifericoResource.Meta):
        model = Mouse

class ImpresoraResource(BasePerifericoResource):
    class Meta(BasePerifericoResource.Meta):
        model = Impresora

class ScanerResource(BasePerifericoResource):
    class Meta(BasePerifericoResource.Meta):
        model = Scaner

class UPSResource(BasePerifericoResource):
    class Meta(BasePerifericoResource.Meta):
        model = UPS 