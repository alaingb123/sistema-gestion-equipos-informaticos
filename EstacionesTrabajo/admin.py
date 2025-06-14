from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import path
from django.shortcuts import render
from django.db import models
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from import_export.admin import ExportMixin
from import_export.formats import base_formats
from .models import PC, Responsable, AreaOrganizativa
from Perifericos.models import Monitor, Teclado, Mouse, Impresora, Scaner, UPS
from ComponentesInternos.models import (SistemaOperativo, Procesador, RAM, DiscoDuro,
                                      NumeroInventario)
from .resources import PCResource, AreaOrganizativaResource, ResponsableResource

# Inlines para PC
class DispositivoBaseInline(admin.TabularInline):
    extra = 1
    can_delete = True
    show_change_link = True
    fields = ('numero_inventario', 'marca', 'funciona', 'es_proyecto_internacional')
    readonly_fields = ('marca', 'funciona', 'es_proyecto_internacional')
    autocomplete_fields = ['numero_inventario']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Sobreescribir el método save del form
        original_init = formset.form.__init__
        def new_init(self_form, *args, **kwargs):
            original_init(self_form, *args, **kwargs)
            if 'numero_inventario' in self_form.initial:
                self_form.fields['numero_inventario'].widget.can_add_related = False
                self_form.fields['numero_inventario'].widget.can_change_related = False

            # Modificar la URL del widget de autocompletado para incluir el tipo de dispositivo
            widget = self_form.fields['numero_inventario'].widget
            # Asegurarse de que es un widget de autocompletado envuelto
            if hasattr(widget, 'widget'):
                autocomplete_widget = widget.widget
                if hasattr(autocomplete_widget, 'url'):
                    base_url = autocomplete_widget.url
                    if '?' in base_url:
                        autocomplete_widget.url = f"{base_url}&model_type={self.model.TIPO_DISPOSITIVO}"
                    else:
                        autocomplete_widget.url = f"{base_url}?model_type={self.model.TIPO_DISPOSITIVO}"

        formset.form.__init__ = new_init
        return formset

class MonitorInline(DispositivoBaseInline):
    model = Monitor
    verbose_name = 'Monitor Asociado'
    verbose_name_plural = 'Monitores Asociados'

class TecladoInline(DispositivoBaseInline):
    model = Teclado
    verbose_name = 'Teclado Asociado'
    verbose_name_plural = 'Teclados Asociados'

class MouseInline(DispositivoBaseInline):
    model = Mouse
    verbose_name = 'Mouse Asociado'
    verbose_name_plural = 'Mouse Asociados'

class ImpresoraInline(DispositivoBaseInline):
    model = Impresora
    verbose_name = 'Impresora Asociada'
    verbose_name_plural = 'Impresoras Asociadas'

class ScanerInline(DispositivoBaseInline):
    model = Scaner
    verbose_name = 'Escáner Asociado'
    verbose_name_plural = 'Escáneres Asociados'

class UPSInline(DispositivoBaseInline):
    model = UPS
    verbose_name = 'UPS Asociado'
    verbose_name_plural = 'UPS Asociados'

class PCAreaSelectFilter(SimpleListFilter):
    title = 'Área Principal'
    parameter_name = 'area_principal'
    template = 'admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        areas = AreaOrganizativa.objects.filter(area_padre__isnull=True).order_by('nombre')
        return [(str(area.id), area.nombre) for area in areas]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                area_id = int(value)
                area_ids = [area_id]
                subareas = AreaOrganizativa.objects.filter(area_padre_id=area_id)
                area_ids.extend(subareas.values_list('id', flat=True))
                for subarea in subareas:
                    sub_subareas = AreaOrganizativa.objects.filter(area_padre_id=subarea.id)
                    area_ids.extend(sub_subareas.values_list('id', flat=True))
                return queryset.filter(area__id__in=area_ids)
            except (ValueError, TypeError):
                return queryset
        return queryset

class PCSubareaSelectFilter(SimpleListFilter):
    title = 'Subárea/Departamento'
    parameter_name = 'subarea'
    template = 'admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        subareas = AreaOrganizativa.objects.filter(
            area_padre__isnull=False,
            area_padre__area_padre__isnull=True
        ).order_by('nombre')
        return [(str(subarea.id), subarea.nombre) for subarea in subareas]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                subarea_id = int(value)
                area_ids = [subarea_id]
                sub_subareas = AreaOrganizativa.objects.filter(area_padre_id=subarea_id)
                area_ids.extend(sub_subareas.values_list('id', flat=True))
                return queryset.filter(area__id__in=area_ids)
            except (ValueError, TypeError):
                return queryset
        return queryset

class PCLocalSelectFilter(SimpleListFilter):
    title = 'Local'
    parameter_name = 'local'
    template = 'admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        locales = AreaOrganizativa.objects.filter(
            area_padre__area_padre__isnull=False
        ).order_by('nombre')
        return [(str(local.id), local.nombre) for local in locales]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                local_id = int(value)
                return queryset.filter(area__id=local_id)
            except (ValueError, TypeError):
                return queryset
        return queryset

class AreaOrganizativaAreaSelectFilter(SimpleListFilter):
    title = 'Área Principal'
    parameter_name = 'area_principal'
    template = 'admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        areas = AreaOrganizativa.objects.filter(area_padre__isnull=True).order_by('nombre')
        return [(str(area.id), area.nombre) for area in areas]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                area_id = int(value)
                area_ids = [area_id]
                subareas = AreaOrganizativa.objects.filter(area_padre_id=area_id)
                area_ids.extend(subareas.values_list('id', flat=True))
                for subarea in subareas:
                    sub_subareas = AreaOrganizativa.objects.filter(area_padre_id=subarea.id)
                    area_ids.extend(sub_subareas.values_list('id', flat=True))
                return queryset.filter(id__in=area_ids)
            except (ValueError, TypeError):
                return queryset
        return queryset

class AreaOrganizativaSubareaSelectFilter(SimpleListFilter):
    title = 'Subárea/Departamento'
    parameter_name = 'subarea'
    template = 'admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        subareas = AreaOrganizativa.objects.filter(
            area_padre__isnull=False,
            area_padre__area_padre__isnull=True
        ).order_by('nombre')
        return [(str(subarea.id), subarea.nombre) for subarea in subareas]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                subarea_id = int(value)
                area_ids = [subarea_id]
                sub_subareas = AreaOrganizativa.objects.filter(area_padre_id=subarea_id)
                area_ids.extend(sub_subareas.values_list('id', flat=True))
                return queryset.filter(id__in=area_ids)
            except (ValueError, TypeError):
                return queryset
        return queryset

class AreaOrganizativaLocalSelectFilter(SimpleListFilter):
    title = 'Local'
    parameter_name = 'local'
    template = 'admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        locales = AreaOrganizativa.objects.filter(
            area_padre__area_padre__isnull=False
        ).order_by('nombre')
        return [(str(local.id), local.nombre) for local in locales]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                local_id = int(value)
                return queryset.filter(id=local_id)
            except (ValueError, TypeError):
                return queryset
        return queryset

class SistemaOperativoSelectFilter(SimpleListFilter):
    title = 'Sistema Operativo'
    parameter_name = 'sistema_operativo'
    template = 'admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        sistemas = SistemaOperativo.objects.all().order_by('nombre')
        return [(str(so.id), so.nombre) for so in sistemas]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                so_id = int(value)
                return queryset.filter(sistema_operativo_id=so_id)
            except (ValueError, TypeError):
                return queryset
        return queryset

class ProcesadorSelectFilter(SimpleListFilter):
    title = 'Procesador'
    parameter_name = 'procesador'
    template = 'admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        procesadores = Procesador.objects.all().order_by('nombre')
        return [(str(proc.id), proc.nombre) for proc in procesadores]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                proc_id = int(value)
                return queryset.filter(procesador_id=proc_id)
            except (ValueError, TypeError):
                return queryset
        return queryset

class RAMSelectFilter(SimpleListFilter):
    title = 'Memoria RAM'
    parameter_name = 'ram'
    template = 'admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        rams = RAM.objects.all().order_by('capacidad')
        return [(str(ram.id), ram.capacidad) for ram in rams]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                ram_id = int(value)
                return queryset.filter(ram_id=ram_id)
            except (ValueError, TypeError):
                return queryset
        return queryset

class DiscoDuroSelectFilter(SimpleListFilter):
    title = 'Disco Duro'
    parameter_name = 'disco_duro'
    template = 'admin/dropdown_filter.html'

    def lookups(self, request, model_admin):
        discos = DiscoDuro.objects.all().order_by('capacidad')
        return [(str(disco.id), disco.capacidad) for disco in discos]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                disco_id = int(value)
                return queryset.filter(disco_duro_id=disco_id)
            except (ValueError, TypeError):
                return queryset
        return queryset

@admin.register(AreaOrganizativa)
class AreaOrganizativaAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = AreaOrganizativaResource
    formats = [base_formats.XLSX]
    list_display = ['get_nombre_completo', 'area_padre', 'get_responsables_info', 'get_pcs_info', 
                    'get_monitores_info', 'get_teclados_info', 'get_mouses_info', 
                    'get_impresoras_info', 'get_scaners_info', 'get_ups_info']
    search_fields = ['nombre', 'area_padre__nombre']
    list_filter = [AreaOrganizativaAreaSelectFilter, AreaOrganizativaSubareaSelectFilter, AreaOrganizativaLocalSelectFilter]
    ordering = ['area_padre__nombre', 'nombre']

    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }

    def get_nombre_completo(self, obj):
        return str(obj)
    get_nombre_completo.short_description = 'Nombre'
    get_nombre_completo.admin_order_field = 'nombre'

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

    def get_responsables_info(self, obj):
        areas = self.get_areas_descendientes(obj)
        count = Responsable.objects.filter(area__id__in=areas).count()
        return count if count > 0 else "-"
    get_responsables_info.short_description = 'Responsables'

    def get_pcs_info(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = PC.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = PC.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"
    get_pcs_info.short_description = 'PCs (OK/Total)'

    def get_monitores_info(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = Monitor.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = Monitor.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"
    get_monitores_info.short_description = 'Monitores (OK/Total)'

    def get_teclados_info(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = Teclado.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = Teclado.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"
    get_teclados_info.short_description = 'Teclados (OK/Total)'

    def get_mouses_info(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = Mouse.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = Mouse.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"
    get_mouses_info.short_description = 'Mouse (OK/Total)'

    def get_impresoras_info(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = Impresora.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = Impresora.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"
    get_impresoras_info.short_description = 'Impresoras (OK/Total)'

    def get_scaners_info(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = Scaner.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = Scaner.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"
    get_scaners_info.short_description = 'Escáneres (OK/Total)'

    def get_ups_info(self, obj):
        areas = self.get_areas_descendientes(obj)
        total = UPS.objects.filter(area__id__in=areas).count()
        if total == 0:
            return "-"
        funcionando = UPS.objects.filter(area__id__in=areas, funciona=True).count()
        return f"{funcionando}/{total}"
    get_ups_info.short_description = 'UPS (OK/Total)'

@admin.register(Responsable)
class ResponsableAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ResponsableResource
    formats = [base_formats.XLSX]
    list_display = ['nombre', 'area', 'get_pcs_info', 'get_monitores_info', 'get_teclados_info', 
                    'get_mouses_info', 'get_impresoras_info', 'get_scaners_info', 'get_ups_info']
    search_fields = ['nombre', 'area__nombre']
    list_filter = [PCAreaSelectFilter, PCSubareaSelectFilter, PCLocalSelectFilter]
    ordering = ['nombre']

    def get_pcs_info(self, obj):
        count = PC.objects.filter(responsable=obj).count()
        return count if count > 0 else "-"
    get_pcs_info.short_description = 'PCs'

    def get_monitores_info(self, obj):
        count = Monitor.objects.filter(responsable=obj).count()
        return count if count > 0 else "-"
    get_monitores_info.short_description = 'Monitores'

    def get_teclados_info(self, obj):
        count = Teclado.objects.filter(responsable=obj).count()
        return count if count > 0 else "-"
    get_teclados_info.short_description = 'Teclados'

    def get_mouses_info(self, obj):
        count = Mouse.objects.filter(responsable=obj).count()
        return count if count > 0 else "-"
    get_mouses_info.short_description = 'Mouse'

    def get_impresoras_info(self, obj):
        count = Impresora.objects.filter(responsable=obj).count()
        return count if count > 0 else "-"
    get_impresoras_info.short_description = 'Impresoras'

    def get_scaners_info(self, obj):
        count = Scaner.objects.filter(responsable=obj).count()
        return count if count > 0 else "-"
    get_scaners_info.short_description = 'Escáneres'

    def get_ups_info(self, obj):
        count = UPS.objects.filter(responsable=obj).count()
        return count if count > 0 else "-"
    get_ups_info.short_description = 'UPS'

@admin.register(PC)
class PCAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = PCResource
    formats = [base_formats.XLSX]
    list_display = ['responsable', 'get_numero_inventario', 'get_area_display', 
                   'get_estado', 'get_proyecto_internacional', 'sistema_operativo', 
                   'procesador', 'ram', 'disco_duro', 'get_monitor', 'get_teclado', 
                   'get_mouse', 'get_impresora', 'get_scaner', 'get_ups']

    list_filter = [
        PCAreaSelectFilter,
        PCSubareaSelectFilter,
        PCLocalSelectFilter,
        SistemaOperativoSelectFilter,
        ProcesadorSelectFilter,
        RAMSelectFilter,
        DiscoDuroSelectFilter,
        'funciona',
        'es_proyecto_internacional',
    ]
    search_fields = ['numero_inventario__codigo', 'responsable__nombre',
                    'area__nombre', 'area__area_padre__nombre']
    autocomplete_fields = ['numero_inventario', 'responsable', 'area',
                          'sistema_operativo', 'procesador', 'ram', 'disco_duro']
    list_per_page = 20

    inlines = [
        MonitorInline,
        TecladoInline,
        MouseInline,
        ImpresoraInline,
        ScanerInline,
        UPSInline,
    ]

    fieldsets = (
        ('Información General', {
            'fields': ('numero_inventario', 'responsable', 'area')
        }),
        ('Estado del Equipo', {
            'fields': ('funciona', 'es_proyecto_internacional')
        }),
        ('Componentes Internos', {
            'fields': ('sistema_operativo', 'procesador', 'ram', 'disco_duro')
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'delete-with-options/<path:object_id>/',
                self.admin_site.admin_view(self.delete_with_options_view),
                name='estacionestrabajo_pc_delete_with_options',
            ),
        ]
        return custom_urls + urls

    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }
        js = ('admin/js/inline_filters.js',)

    def delete_view(self, request, object_id, extra_context=None):
        """Sobreescribimos el delete_view para redirigir a nuestra vista personalizada"""
        return HttpResponseRedirect(f'../delete-with-options/{object_id}/')

    def delete_with_options_view(self, request, object_id):
        """Vista personalizada para eliminar PC con opciones para periféricos"""
        pc = self.get_object(request, object_id)
        
        if request.method == 'POST':
            if 'confirm' in request.POST:
                # Obtener los periféricos que el usuario quiere eliminar
                delete_monitor = 'delete_monitor' in request.POST
                delete_teclado = 'delete_teclado' in request.POST
                delete_mouse = 'delete_mouse' in request.POST
                delete_impresora = 'delete_impresora' in request.POST
                delete_scaner = 'delete_scaner' in request.POST
                delete_ups = 'delete_ups' in request.POST

                # Eliminar los periféricos seleccionados
                if delete_monitor:
                    pc.monitor_set.all().delete()
                if delete_teclado:
                    pc.teclado_set.all().delete()
                if delete_mouse:
                    pc.mouse_set.all().delete()
                if delete_impresora:
                    pc.impresora_set.all().delete()
                if delete_scaner:
                    pc.scaner_set.all().delete()
                if delete_ups:
                    pc.ups_set.all().delete()

                # Eliminar la PC
                pc.delete()
                
                self.message_user(request, 'La PC y los periféricos seleccionados han sido eliminados.')
                return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

        # Preparar el contexto con los periféricos asociados
        perifericos = {
            'monitores': pc.monitor_set.all(),
            'teclados': pc.teclado_set.all(),
            'mouses': pc.mouse_set.all(),
            'impresoras': pc.impresora_set.all(),
            'scaners': pc.scaner_set.all(),
            'ups': pc.ups_set.all(),
        }

        context = {
            'title': f'¿Eliminar {pc}?',
            'object': pc,
            'perifericos': perifericos,
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
            **self.admin_site.each_context(request),
        }

        return render(request, 'admin/estacionestrabajo/pc/delete_with_options.html', context)

    def get_numero_inventario(self, obj):
        if obj.numero_inventario:
            return obj.numero_inventario.codigo
        return "Sin número"
    get_numero_inventario.short_description = 'No. Inventario'

    def get_estado(self, obj):
        if obj.funciona:
            return format_html('<span style="color: green;">✔</span>')
        return format_html('<span style="color: red;">✘</span>')
    get_estado.short_description = 'Estado'

    def get_proyecto_internacional(self, obj):
        return "SI" if obj.es_proyecto_internacional else "NO"
    get_proyecto_internacional.short_description = 'Proyecto'

    def get_monitor(self, obj):
        monitor = obj.monitor_set.first()
        if monitor:
            if monitor.numero_inventario:
                return monitor.numero_inventario.codigo
            return f"Marca: {monitor.marca}"
        return "-"
    get_monitor.short_description = 'Monitor'

    def get_teclado(self, obj):
        teclado = obj.teclado_set.first()
        if teclado:
            if teclado.numero_inventario:
                return teclado.numero_inventario.codigo
            return f"Marca: {teclado.marca}"
        return "-"
    get_teclado.short_description = 'Teclado'

    def get_mouse(self, obj):
        mouse = obj.mouse_set.first()
        if mouse:
            if mouse.numero_inventario:
                return mouse.numero_inventario.codigo
            return f"Marca: {mouse.marca}"
        return "-"
    get_mouse.short_description = 'Mouse'

    def get_impresora(self, obj):
        impresora = obj.impresora_set.first()
        if impresora:
            if impresora.numero_inventario:
                return impresora.numero_inventario.codigo
            return f"Marca: {impresora.marca}"
        return "-"
    get_impresora.short_description = 'Impresora'

    def get_scaner(self, obj):
        scaner = obj.scaner_set.first()
        if scaner:
            if scaner.numero_inventario:
                return scaner.numero_inventario.codigo
            return f"Marca: {scaner.marca}"
        return "-"
    get_scaner.short_description = 'Escáner'

    def get_ups(self, obj):
        ups = obj.ups_set.first()
        if ups:
            if ups.numero_inventario:
                return ups.numero_inventario.codigo
            return f"Marca: {ups.marca}"
        return "-"
    get_ups.short_description = 'UPS'

    def get_area_display(self, obj):
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
            return format_html('<span title="{0}">{1}</span>', area_completa, obj.area.nombre)
        return "Sin área"
    get_area_display.short_description = 'Área'
    get_area_display.admin_order_field = 'area__area_padre__area_padre__nombre'

class DispositivoAdmin(admin.ModelAdmin):
    list_display = ['get_numero_inventario', 'get_responsable', 'get_area_display', 'get_pc', 
                   'get_estado', 'get_proyecto_internacional', 'marca']
    list_filter = [
        PCAreaSelectFilter,
        PCSubareaSelectFilter,
        PCLocalSelectFilter,
        'funciona', 
        'es_proyecto_internacional', 
        'pc_asociada', 
        'responsable'
    ]
    search_fields = ['numero_inventario__codigo', 'pc_asociada__numero_inventario__codigo',
                    'marca', 'responsable__nombre', 'area__nombre', 
                    'area__area_padre__nombre', 'area__area_padre__area_padre__nombre']
    autocomplete_fields = ['numero_inventario', 'pc_asociada', 'responsable', 'area']
    list_per_page = 20

    def get_area_display(self, obj):
        if obj.area:
            # Construir la ruta jerárquica completa
            if obj.area.area_padre:
                if obj.area.area_padre.area_padre:
                    # Tercer nivel (Local)
                    return f"{obj.area.area_padre.area_padre.nombre} - {obj.area.area_padre.nombre} - {obj.area.nombre}"
                # Segundo nivel (Departamento)
                return f"{obj.area.area_padre.nombre} - {obj.area.nombre}"
            # Primer nivel (Área principal)
            return obj.area.nombre
        return "Sin área"
    get_area_display.short_description = 'Área'
    get_area_display.admin_order_field = 'area__area_padre__area_padre__nombre'






admin.site.site_header = "Equipos Informáticos"
admin.site.site_title = "Equipos Informáticos"
admin.site.index_title = "Bienvenido al Panel de Administración"
