import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from EstacionesTrabajo.models import PC
from ComponentesInternos.models import SistemaOperativo, NumeroInventario

class Command(BaseCommand):
    help = 'Asigna sistemas operativos a PCs desde un archivo Excel'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_path',
            type=str,
            nargs='?',  # Hace el argumento opcional
            default='sistemas.xlsx',  # Valor por defecto
            help='Ruta al archivo Excel (por defecto: sistemas.xlsx en la raíz del proyecto)'
        )

    def handle(self, *args, **options):
        excel_path = options['excel_path']
        
        try:
            # Leer el Excel
            df = pd.read_excel(excel_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error leyendo el archivo Excel: {str(e)}'))
            return

        # Mapeo de columnas a nombres de sistemas operativos
        sistemas = {
            'W7': 'Windows 7',
            'W8': 'Windows 8',
            'W8.1': 'Windows 8.1',
            'W10': 'Windows 10',
            'W11': 'Windows 11'
        }
        
        # Contador para estadísticas
        stats = {
            'pcs_encontradas': 0,
            'pcs_no_encontradas': 0,
            'sistemas_asignados': 0
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
                    
                    # Buscar qué sistema operativo tiene marcado (valor 1)
                    sistema_encontrado = False
                    for col, nombre_sistema in sistemas.items():
                        if row[col] == 1:
                            # Obtener o crear el sistema operativo
                            sistema, created = SistemaOperativo.objects.get_or_create(
                                nombre=nombre_sistema
                            )
                            
                            # Asignar el sistema operativo a la PC
                            pc.sistema_operativo = sistema
                            pc.save()
                            
                            self.stdout.write(self.style.SUCCESS(
                                f"✅ PC {num_inventario}: Asignado {nombre_sistema}"
                            ))
                            stats['sistemas_asignados'] += 1
                            sistema_encontrado = True
                            break
                    
                    if not sistema_encontrado:
                        self.stdout.write(self.style.WARNING(
                            f"⚠️ PC {num_inventario}: No tiene sistema operativo marcado"
                        ))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"❌ Error procesando PC {num_inventario}: {str(e)}"
                    ))
        
        # Mostrar estadísticas
        self.stdout.write("\n=== Estadísticas ===")
        self.stdout.write(self.style.SUCCESS(f"PCs encontradas: {stats['pcs_encontradas']}"))
        self.stdout.write(self.style.WARNING(f"PCs no encontradas: {stats['pcs_no_encontradas']}"))
        self.stdout.write(self.style.SUCCESS(f"Sistemas operativos asignados: {stats['sistemas_asignados']}")) 