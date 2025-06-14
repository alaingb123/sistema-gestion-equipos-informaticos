from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from import_export.admin import ExportMixin
from import_export.formats import base_formats
from .models import Monitor, Teclado, Mouse, Impresora, Scaner, UPS
from EstacionesTrabajo.models import AreaOrganizativa
from .resources import (MonitorResource, TecladoResource, MouseResource, 
                      ImpresoraResource, ScanerResource, UPSResource)
from EstacionesTrabajo.admin import PCAreaSelectFilter, PCSubareaSelectFilter, PCLocalSelectFilter


class AreaSelectFilter(SimpleListFilter):
    title = 'Área'
    parameter_name = 'area'
    template = 'admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        areas = AreaOrganizativa.objects.filter(area_padre__isnull=True).order_by('nombre')
        return [(str(area.id), area.nombre) for area in areas]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                area_id = int(value)
                # Incluir el área seleccionada y todas sus subáreas y sub-subáreas
                area_ids = [area_id]
                # Obtener subáreas directas
                subareas = AreaOrganizativa.objects.filter(area_padre_id=area_id)
                area_ids.extend(subareas.values_list('id', flat=True))
                # Obtener sub-subáreas
                for subarea in subareas:
                    sub_subareas = AreaOrganizativa.objects.filter(area_padre_id=subarea.id)
                    area_ids.extend(sub_subareas.values_list('id', flat=True))
                return queryset.filter(area_id__in=area_ids)
            except (ValueError, TypeError):
                return queryset
        return queryset

class SubareaSelectFilter(SimpleListFilter):
    title = 'Subárea/Departamento'
    parameter_name = 'subarea'
    template = 'admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        # Filtrar solo las subáreas que son hijas directas de áreas principales
        subareas = AreaOrganizativa.objects.filter(
            area_padre__isnull=False,
            area_padre__area_padre__isnull=True
        ).order_by('area_padre__nombre', 'nombre')
        return [(str(subarea.id), subarea.nombre) for subarea in subareas]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                subarea_id = int(value)
                # Incluir la subárea seleccionada y sus sub-subáreas
                area_ids = [subarea_id]
                sub_subareas = AreaOrganizativa.objects.filter(area_padre_id=subarea_id)
                area_ids.extend(sub_subareas.values_list('id', flat=True))
                return queryset.filter(area_id__in=area_ids)
            except (ValueError, TypeError):
                return queryset
        return queryset

class LocalSelectFilter(SimpleListFilter):
    title = 'Local'
    parameter_name = 'local'
    template = 'admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        # Filtrar solo las áreas que son de tercer nivel (locales)
        locales = AreaOrganizativa.objects.filter(
            area_padre__area_padre__isnull=False
        ).order_by('area_padre__area_padre__nombre', 'area_padre__nombre', 'nombre')
        return [(str(local.id), local.nombre) for local in locales]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                local_id = int(value)
                return queryset.filter(area_id=local_id)
            except (ValueError, TypeError):
                return queryset
        return queryset

class DispositivoAdmin(admin.ModelAdmin):
    list_display = ['get_numero_inventario', 'get_responsable', 'get_area', 'get_pc', 
                   'get_estado', 'get_proyecto_internacional', 'marca']
    list_filter = [
        PCAreaSelectFilter,
    PCSubareaSelectFilter,
    PCLocalSelectFilter,
        'funciona', 
        'es_proyecto_internacional', 
    ]
    search_fields = ['numero_inventario__codigo', 'pc_asociada__numero_inventario__codigo',
                    'marca', 'responsable__nombre', 'area__nombre', 
                    'area__area_padre__nombre', 'area__area_padre__area_padre__nombre']
    autocomplete_fields = ['numero_inventario', 'pc_asociada', 'responsable', 'area']
    list_per_page = 20

    fieldsets = (
        ('Información del Dispositivo', {
            'fields': ('numero_inventario', 'marca')
        }),
        ('Asignación', {
            'fields': ('pc_asociada', ('responsable', 'area')),
            'description': 'Si asigna una PC, el responsable y área se tomarán automáticamente de la PC. '
                         'Si desea asignar un responsable o área diferente, primero guarde el dispositivo '
                         'y luego modifique estos campos.'
        }),
        ('Estado', {
            'fields': ('funciona', 'es_proyecto_internacional')
        }),
    )

    def get_numero_inventario(self, obj):
        if obj.numero_inventario:
            return obj.numero_inventario.codigo
        return "Sin número"
    get_numero_inventario.short_description = 'No. Inventario'

    def get_pc(self, obj):
        if obj.pc_asociada and obj.pc_asociada.numero_inventario:
            return obj.pc_asociada.numero_inventario.codigo
        return "Sin estación asociada"
    get_pc.short_description = 'Estación Asociada'

    def get_responsable(self, obj):
        if obj.responsable:
            if obj.pc_asociada and obj.responsable == obj.pc_asociada.responsable:
                return format_html('<span title="Heredado de PC">👤 {}</span>', obj.responsable.nombre)
            return obj.responsable.nombre
        return "Sin responsable"
    get_responsable.short_description = 'Responsable'

    def get_area(self, obj):
        if obj.area:
            # Construir la ruta jerárquica completa para el título
            if obj.area.area_padre:
                if obj.area.area_padre.area_padre:
                    # Tercer nivel (Local)
                    area_completa = f"{obj.area.area_padre.area_padre.nombre} - {obj.area.area_padre.nombre} - {obj.area.nombre}"
                else:
                    # Segundo nivel (Departamento)
                    area_completa = f"{obj.area.area_padre.nombre} - {obj.area.nombre}"
            else:
                # Primer nivel (Área principal)
                area_completa = obj.area.nombre

            # Para el display, mostrar solo el nombre del área más específica
            if obj.pc_asociada and obj.area == obj.pc_asociada.area:
                return format_html('<span title="{0}">🏢 {1}</span>', area_completa, obj.area.nombre)
            return format_html('<span title="{0}">{1}</span>', area_completa, obj.area.nombre)
        return "Sin área"
    get_area.short_description = 'Área'
    get_area.admin_order_field = 'area__area_padre__area_padre__nombre'

    def get_estado(self, obj):
        if obj.funciona:
            return format_html('<span style="color: green;">✔</span>')
        return format_html('<span style="color: red;">✘</span>')
    get_estado.short_description = 'Estado'

    def get_proyecto_internacional(self, obj):
        return "SI" if obj.es_proyecto_internacional else "NO"
    get_proyecto_internacional.short_description = 'Proyecto'

@admin.register(Monitor)
class MonitorAdmin(ExportMixin, DispositivoAdmin):
    resource_class = MonitorResource
    formats = [base_formats.XLSX]

@admin.register(Teclado)
class TecladoAdmin(ExportMixin, DispositivoAdmin):
    resource_class = TecladoResource
    formats = [base_formats.XLSX]

@admin.register(Mouse)
class MouseAdmin(ExportMixin, DispositivoAdmin):
    resource_class = MouseResource
    formats = [base_formats.XLSX]

@admin.register(Impresora)
class ImpresoraAdmin(ExportMixin, DispositivoAdmin):
    resource_class = ImpresoraResource
    formats = [base_formats.XLSX]

@admin.register(Scaner)
class ScanerAdmin(ExportMixin, DispositivoAdmin):
    resource_class = ScanerResource
    formats = [base_formats.XLSX]

@admin.register(UPS)
class UPSAdmin(ExportMixin, DispositivoAdmin):
    resource_class = UPSResource
    formats = [base_formats.XLSX]
