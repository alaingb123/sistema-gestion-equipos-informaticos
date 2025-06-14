from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, BooleanWidget
from .models import PC, AreaOrganizativa, Responsable
from Perifericos.models import Monitor, Teclado, Mouse, Impresora, Scaner, UPS
from ComponentesInternos.models import NumeroInventario, SistemaOperativo, Procesador, RAM, DiscoDuro
from django.db.models import Count

class SiNoWidget(BooleanWidget):
    def render(self, value, obj=None, **kwargs):
        return 'SI' if value else 'NO'

class PCResource(resources.ModelResource):
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
    sistema_operativo = fields.Field(
        column_name='Sistema Op.',
        attribute='sistema_operativo',
        widget=ForeignKeyWidget(SistemaOperativo, 'nombre')
    )
    procesador = fields.Field(
        column_name='CPU',
        attribute='procesador',
        widget=ForeignKeyWidget(Procesador, 'nombre')
    )
    ram = fields.Field(
        column_name='RAM',
        attribute='ram',
        widget=ForeignKeyWidget(RAM, 'capacidad')
    )
    disco_duro = fields.Field(
        column_name='HDD',
        attribute='disco_duro',
        widget=ForeignKeyWidget(DiscoDuro, 'capacidad')
    )

    class Meta:
        model = PC
        fields = ('numero_inventario', 'responsable', 'area', 'funciona', 
                 'es_proyecto_internacional', 'sistema_operativo', 'procesador', 
                 'ram', 'disco_duro')
        export_order = fields

class AreaOrganizativaResource(resources.ModelResource):
    area_padre = fields.Field(
        column_name='Área Principal',
        attribute='area_padre',
        widget=ForeignKeyWidget(AreaOrganizativa, 'nombre')
    )
    nombre = fields.Field(
        column_name='Nombre Área',
        attribute='nombre'
    )
    responsables = fields.Field(
        column_name='Responsables',
        attribute=None
    )
    pcs = fields.Field(
        column_name='PCs (OK/Total)',
        attribute=None
    )
    monitores = fields.Field(
        column_name='Monitores (OK/Total)',
        attribute=None
    )
    teclados = fields.Field(
        column_name='Teclados (OK/Total)',
        attribute=None
    )
    mouses = fields.Field(
        column_name='Mouse (OK/Total)',
        attribute=None
    )
    impresoras = fields.Field(
        column_name='Impresoras (OK/Total)',
        attribute=None
    )
    scaners = fields.Field(
        column_name='Escáneres (OK/Total)',
        attribute=None
    )
    ups = fields.Field(
        column_name='UPS (OK/Total)',
        attribute=None
    )
    
    def get_areas_descendientes(self, obj):
        """Obtiene todas las áreas descendientes (hijas y nietas)"""
        areas = [obj.id]
        # Obtener áreas hijas
        hijas = AreaOrganizativa.objects.filter(area_padre=obj)
        for hija in hijas:
            areas.append(hija.id)
            # Obtener áreas nietas
            nietas = AreaOrganizativa.objects.filter(area_padre=hija)
            areas.extend(nietas.values_list('id', flat=True))
        return areas

    def dehydrate_responsables(self, obj):
        areas = self.get_areas_descendientes(obj)
        count = Responsable.objects.filter(area__id__in=areas).count()
        return count if count > 0 else "-"

    def dehydrate_pcs(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = PC.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = PC.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"

    def dehydrate_monitores(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = Monitor.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = Monitor.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"

    def dehydrate_teclados(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = Teclado.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = Teclado.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"

    def dehydrate_mouses(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = Mouse.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = Mouse.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"

    def dehydrate_impresoras(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = Impresora.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = Impresora.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"

    def dehydrate_scaners(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = Scaner.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = Scaner.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"

    def dehydrate_ups(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = UPS.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = UPS.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"

    class Meta:
        model = AreaOrganizativa
        fields = ('nombre', 'area_padre', 'responsables', 'pcs', 'monitores', 
                 'teclados', 'mouses', 'impresoras', 'scaners', 'ups')
        export_order = fields

class ResponsableResource(resources.ModelResource):
    area = fields.Field(
        column_name='Área',
        attribute='area',
        widget=ForeignKeyWidget(AreaOrganizativa, 'nombre')
    )
    nombre = fields.Field(
        column_name='Nombre Responsable',
        attribute='nombre'
    )

    class Meta:
        model = Responsable
        fields = ('nombre', 'area')
        export_order = fields 