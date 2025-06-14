document.addEventListener('DOMContentLoaded', function() {
    // Función para modificar la URL del Select2 para incluir el tipo de dispositivo
    function modifySelect2Url(select, tipo) {
        if (!select.classList.contains('select2-hidden-accessible')) {
            django.jQuery(select).select2({
                ajax: {
                    url: '/admin/get-numeros-inventario/',
                    dataType: 'json',
                    delay: 250,
                    data: function(params) {
                        return {
                            term: params.term,
                            tipo: tipo,
                        };
                    },
                    processResults: function(data) {
                        return {
                            results: data.results,
                            pagination: data.pagination
                        };
                    },
                    cache: true
                },
                minimumInputLength: 1,
                placeholder: 'Buscar número de inventario...',
                language: {
                    inputTooShort: function() {
                        return "Por favor ingrese 1 o más caracteres";
                    },
                    noResults: function() {
                        return "No se encontraron resultados";
                    },
                    searching: function() {
                        return "Buscando...";
                    }
                }
            });
        }
    }

    // Función para inicializar el filtrado en los inlines
    function initializeInlineFilters() {
        // Monitores
        document.querySelectorAll('.inline-group[id*="monitor"] .inline-related:not(.empty-form) select[name*="numero_inventario"]').forEach(select => {
            modifySelect2Url(select, 'Monitor');
        });
        
        // Teclados
        document.querySelectorAll('.inline-group[id*="teclado"] .inline-related:not(.empty-form) select[name*="numero_inventario"]').forEach(select => {
            modifySelect2Url(select, 'Teclado');
        });
        
        // Mouse
        document.querySelectorAll('.inline-group[id*="mouse"] .inline-related:not(.empty-form) select[name*="numero_inventario"]').forEach(select => {
            modifySelect2Url(select, 'Mouse');
        });
        
        // Impresoras
        document.querySelectorAll('.inline-group[id*="impresora"] .inline-related:not(.empty-form) select[name*="numero_inventario"]').forEach(select => {
            modifySelect2Url(select, 'Impresora');
        });
        
        // Scaners
        document.querySelectorAll('.inline-group[id*="scaner"] .inline-related:not(.empty-form) select[name*="numero_inventario"]').forEach(select => {
            modifySelect2Url(select, 'Scanner');
        });
        
        // UPS
        document.querySelectorAll('.inline-group[id*="ups"] .inline-related:not(.empty-form) select[name*="numero_inventario"]').forEach(select => {
            modifySelect2Url(select, 'UPS');
        });
    }

    // Inicializar al cargar la página
    initializeInlineFilters();

    // Observar cambios en los inlines (cuando se agrega uno nuevo)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach(node => {
                    if (node.classList && node.classList.contains('inline-related')) {
                        const inlineGroup = node.closest('.inline-group');
                        if (!inlineGroup) return;

                        const select = node.querySelector('select[name*="numero_inventario"]');
                        if (!select) return;

                        if (inlineGroup.id.includes('monitor')) {
                            modifySelect2Url(select, 'Monitor');
                        } else if (inlineGroup.id.includes('teclado')) {
                            modifySelect2Url(select, 'Teclado');
                        } else if (inlineGroup.id.includes('mouse')) {
                            modifySelect2Url(select, 'Mouse');
                        } else if (inlineGroup.id.includes('impresora')) {
                            modifySelect2Url(select, 'Impresora');
                        } else if (inlineGroup.id.includes('scaner')) {
                            modifySelect2Url(select, 'Scanner');
                        } else if (inlineGroup.id.includes('ups')) {
                            modifySelect2Url(select, 'UPS');
                        }
                    }
                });
            }
        });
    });

    // Observar cambios en todos los grupos de inlines
    document.querySelectorAll('.inline-group').forEach(group => {
        observer.observe(group, { childList: true, subtree: true });
    });
}); 