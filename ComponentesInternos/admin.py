from django.contrib import admin
from import_export.admin import ExportMixin
from import_export.formats import base_formats
from .models import (
    NumeroInventario, SistemaOperativo, Procesador,
    RAM, DiscoDuro
)
from .resources import (NumeroInventarioResource, SistemaOperativoResource, 
                      ProcesadorResource, RAMResource, DiscoDuroResource)
from django.db.models import Q
from django.apps import apps

@admin.register(NumeroInventario)
class NumeroInventarioAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = NumeroInventarioResource
    formats = [base_formats.XLSX]
    list_display = ['codigo', 'tipo_dispositivo', 'get_responsable']
    search_fields = ['codigo']
    list_filter = ['tipo_dispositivo']
    ordering = ['codigo']

    def get_responsable(self, obj):
        dispositivo = obj.get_dispositivo()
        if dispositivo and dispositivo.responsable:
            return dispositivo.responsable
        return "-"
    get_responsable.short_description = 'Responsable'

    def get_search_results(self, request, queryset, search_term):
        print(f"\nBúsqueda iniciada con término: {search_term}")
        
        # Si no hay término de búsqueda, retornamos el queryset original
        if not search_term:
            return queryset, False

        # Si estamos en un autocomplete
        if request.path.endswith('/autocomplete/'):
            print("Estamos en autocomplete")
            # Obtenemos el tipo de modelo del parámetro model_name
            model_name = request.GET.get('model_name', '').capitalize()
            print(f"Nombre del modelo: {model_name}")
            
            if model_name:
                # Convertimos el nombre del modelo a tipo de dispositivo
                model_type = model_name.capitalize()
                print(f"Tipo de dispositivo: {model_type}")
                
                # Primero filtramos por tipo
                queryset = queryset.filter(
                    Q(tipo_dispositivo__isnull=True) | Q(tipo_dispositivo=model_type)
                )
                
                # Creamos un queryset vacío para los resultados
                resultados = self.model.objects.none()
                
                try:
                    # Buscar por código
                    qs_codigo = queryset.filter(codigo__icontains=search_term)
                    print(f"Resultados por código: {qs_codigo.count()}")
                    resultados = resultados | qs_codigo
                    
                    # Buscar por responsable
                    app_label = 'Perifericos' if model_type != 'PC' else 'EstacionesTrabajo'
                    model_class = 'Scaner' if model_type == 'Scanner' else model_type
                    print(f"Buscando en modelo: {app_label}.{model_class}")
                    
                    modelo = apps.get_model(app_label, model_class)
                    
                    # Primero obtenemos los dispositivos que tienen responsables que coinciden
                    dispositivos_con_responsable = modelo.objects.filter(
                        responsable__nombre__icontains=search_term,
                        numero_inventario__isnull=False
                    )
                    print(f"Dispositivos encontrados por responsable: {dispositivos_con_responsable.count()}")
                    
                    # Luego obtenemos sus números de inventario
                    if dispositivos_con_responsable.exists():
                        nums_por_responsable = dispositivos_con_responsable.values_list('numero_inventario', flat=True)
                        qs_responsable = queryset.filter(id__in=nums_por_responsable)
                        print(f"Números de inventario por responsable: {qs_responsable.count()}")
                        resultados = resultados | qs_responsable
                    
                    print(f"Total resultados combinados: {resultados.count()}")
                    return resultados.distinct(), True
                    
                except Exception as e:
                    print(f"Error en búsqueda: {str(e)}")
                    return queryset, False
            
        # Si no estamos en autocomplete, hacemos la búsqueda normal
        return super().get_search_results(request, queryset, search_term)

class ComponenteBaseAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']
    ordering = ['nombre']

@admin.register(SistemaOperativo)
class SistemaOperativoAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = SistemaOperativoResource
    formats = [base_formats.XLSX]
    list_display = ['nombre']
    search_fields = ['nombre']

@admin.register(Procesador)
class ProcesadorAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ProcesadorResource
    formats = [base_formats.XLSX]
    list_display = ['nombre']
    search_fields = ['nombre']

@admin.register(RAM)
class RAMAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = RAMResource
    formats = [base_formats.XLSX]
    list_display = ['capacidad']
    search_fields = ['capacidad']

@admin.register(DiscoDuro)
class DiscoDuroAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = DiscoDuroResource
    formats = [base_formats.XLSX]
    list_display = ['capacidad']
    search_fields = ['capacidad']
