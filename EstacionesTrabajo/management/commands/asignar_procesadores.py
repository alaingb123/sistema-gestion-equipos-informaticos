import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from EstacionesTrabajo.models import PC
from ComponentesInternos.models import Procesador, NumeroInventario

class Command(BaseCommand):
    help = 'Asigna procesadores a PCs desde un archivo Excel'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_path',
            type=str,
            nargs='?',
            default='procesador.xlsx',
            help='Ruta al archivo Excel (por defecto: procesador.xlsx en la raíz del proyecto)'
        )

    def handle(self, *args, **options):
        excel_path = options['excel_path']
        
        try:
            # Leer el Excel
            df = pd.read_excel(excel_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error leyendo el archivo Excel: {str(e)}'))
            return

        # Mapeo de columnas a nombres de procesadores
        procesadores = {
            'celeron': 'Celeron',
            'Pentium III': 'Pentium III',
            'Pentium IV': 'Pentium IV',
            'Dual Core': 'Dual Core',
            'Duo': 'Core 2 Duo',
            'Core I3': 'Core i3',
            'Core I5': 'Core i5',
            'Core I7': 'Core i7',
            'Xeon': 'Xeon',
            'AMD': 'AMD',
            'ATOM': 'Atom',
            'Pentium Gold': 'Pentium Gold',
            'Pentium G20/30': 'Pentium G20/30'
        }
        
        # Contador para estadísticas
        stats = {
            'pcs_encontradas': 0,
            'pcs_no_encontradas': 0,
            'procesadores_asignados': 0
        }
        
        # Procesar cada fila dentro de una transacción
        with transaction.atomic():
            for index, row in df.iterrows():
                num_inventario = str(row['# Inventario']).strip()
                
                try:
                    # Buscar la PC por número de inventario
                    numero_inv = NumeroInventario.objects.filter(codigo=num_inventario).first()
                    if not numero_inv:
                        self.stdout.write(self.style.WARNING(
                            f"❌ No se encontró PC con número de inventario: {num_inventario}"
                        ))
                        stats['pcs_no_encontradas'] += 1
                        continue
                        
                    pc = PC.objects.filter(numero_inventario=numero_inv).first()
                    if not pc:
                        self.stdout.write(self.style.WARNING(
                            f"❌ No se encontró PC con número de inventario: {num_inventario}"
                        ))
                        stats['pcs_no_encontradas'] += 1
                        continue
                    
                    stats['pcs_encontradas'] += 1
                    
                    # Buscar qué procesador tiene marcado (valor 1)
                    procesador_encontrado = False
                    for col, nombre_procesador in procesadores.items():
                        if row[col] == 1:
                            # Obtener o crear el procesador
                            procesador, created = Procesador.objects.get_or_create(
                                nombre=nombre_procesador
                            )
                            
                            # Asignar el procesador a la PC
                            pc.procesador = procesador
                            pc.save()
                            
                            self.stdout.write(self.style.SUCCESS(
                                f"✅ PC {num_inventario}: Asignado {nombre_procesador}"
                            ))
                            stats['procesadores_asignados'] += 1
                            procesador_encontrado = True
                            break
                    
                    if not procesador_encontrado:
                        self.stdout.write(self.style.WARNING(
                            f"⚠️ PC {num_inventario}: No tiene procesador marcado"
                        ))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"❌ Error procesando PC {num_inventario}: {str(e)}"
                    ))
        
        # Mostrar estadísticas
        self.stdout.write("\n=== Estadísticas ===")
        self.stdout.write(self.style.SUCCESS(f"PCs encontradas: {stats['pcs_encontradas']}"))
        self.stdout.write(self.style.WARNING(f"PCs no encontradas: {stats['pcs_no_encontradas']}"))
        self.stdout.write(self.style.SUCCESS(f"Procesadores asignados: {stats['procesadores_asignados']}")) 