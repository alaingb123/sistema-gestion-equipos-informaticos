from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from ComponentesInternos.models import NumeroInventario
from Perifericos.models import Monitor, Teclado, Mouse, Impresora, Scaner, UPS

# Create your views here.

@staff_member_required
def get_numeros_inventario(request):
    """Vista para obtener números de inventario filtrados por tipo"""
    tipo = request.GET.get('tipo')
    term = request.GET.get('term', '')  # Select2 usa 'term' para la búsqueda
    
    if not tipo:
        return JsonResponse({'error': 'Tipo de dispositivo no especificado'}, status=400)
    
    # Filtrar por tipo
    queryset = NumeroInventario.objects.filter(tipo_dispositivo=tipo)
    
    # Excluir los que ya están asignados según el tipo
    if tipo == 'Monitor':
        queryset = queryset.exclude(monitor__isnull=False)
    elif tipo == 'Teclado':
        queryset = queryset.exclude(teclado__isnull=False)
    elif tipo == 'Mouse':
        queryset = queryset.exclude(mouse__isnull=False)
    elif tipo == 'Impresora':
        queryset = queryset.exclude(impresora__isnull=False)
    elif tipo == 'Scanner':
        queryset = queryset.exclude(scaner__isnull=False)
    elif tipo == 'UPS':
        queryset = queryset.exclude(ups__isnull=False)
    
    # Filtrar por búsqueda si se proporciona
    if term:
        queryset = queryset.filter(codigo__icontains=term)
    
    # Limitar a 10 resultados para no sobrecargar
    results = [{'id': num.id, 'text': num.codigo} for num in queryset[:10]]
    
    # Formato esperado por Select2
    return JsonResponse({
        'results': results,
        'pagination': {
            'more': False  # True si hay más resultados disponibles
        }
    })
