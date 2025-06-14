from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import NumeroInventario, SistemaOperativo, Procesador, RAM, DiscoDuro

class NumeroInventarioResource(resources.ModelResource):
    class Meta:
        model = NumeroInventario
        fields = ('codigo',)
        export_order = fields

class SistemaOperativoResource(resources.ModelResource):
    class Meta:
        model = SistemaOperativo
        fields = ('nombre',)
        export_order = fields

class ProcesadorResource(resources.ModelResource):
    class Meta:
        model = Procesador
        fields = ('nombre',)
        export_order = fields

class RAMResource(resources.ModelResource):
    class Meta:
        model = RAM
        fields = ('capacidad',)
        export_order = fields

class DiscoDuroResource(resources.ModelResource):
    class Meta:
        model = DiscoDuro
        fields = ('capacidad',)
        export_order = fields 