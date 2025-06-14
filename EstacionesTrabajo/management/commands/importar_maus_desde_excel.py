from django.core.management.base import BaseCommand
from EstacionesTrabajo.models import AreaOrganizativa, Responsable
from ComponentesInternos.models import NumeroInventario
from Perifericos.models import Mouse
import openpyxl
import os

def normalizar_nombre(nombre):
    if not nombre:
        return nombre
    # Convertir a string si no lo es
    nombre = str(nombre)
    # Eliminar espacios extra y convertir a título
    nombre = ' '.join(nombre.split()).strip()
    # Manejar casos especiales
    nombre = nombre.replace(' (nuevo)', '')
    nombre = nombre.replace(' (Nuevo)', '')
    return nombre

class Command(BaseCommand):
    help = 'Importa los mouse desde un archivo Excel'

    def handle(self, *args, **options):
        self.stdout.write('Importando mouse desde Excel...')

        # Diccionario para contar ocurrencias de códigos
        codigos_contador = {}
        
        # Mapeo de nombres de áreas (para manejar variaciones)
        mapeo_areas = {
            'Subdelegación de CTI': 'Subdelegación CTI',
            'Subdelegación de Medio Ambiente': 'Subdelegación Medio Ambiente',
            'Subdelegación de MA': 'Subdelegación MA'
        }

        # Definir la estructura jerárquica
        estructura = {
            'Oficina de la delegada': [
                'EM Encucijada',
                'EM Camajuaní',
                'EM Remedios',
                'EM Cifuentes',
                'EM Manicaragua',
                'EM Placetas',
                'EM Santo Domingo',
                'EM Corralillo',
                'EM Quemado',
                'EM Ranchuelo',
                'EM Sagua',
                'EM Santa Clara',
                'EM Caibarién'
            ],
            'Subdelegación OCIA': [
                'Departamento OCAI',
                'Departamento Gestión Documental y Archivo'
            ],
            'Dirección Administrativa': [
                'Economía',
                'Aseguramiento',
                'Recursos Humanos'
            ],
            'Subdelegación CTI': [],
            'Subdelegación Medio Ambiente': [],
      
        }

        # Crear áreas y sus departamentos
        areas = {}
        for area_nombre, departamentos in estructura.items():
            # Crear área principal
            area_obj, created = AreaOrganizativa.objects.get_or_create(
                nombre=area_nombre,
                area_padre=None
            )
            areas[area_nombre] = area_obj
            if created:
                self.stdout.write(f'  + Creada área principal: {area_nombre}')
            else:
                self.stdout.write(f'  ✓ Área principal existente: {area_nombre}')

            # Crear departamentos/subáreas
            for depto_nombre in departamentos:
                depto_obj, created = AreaOrganizativa.objects.get_or_create(
                    nombre=depto_nombre,
                    area_padre=area_obj
                )
                areas[f"{area_nombre} ({depto_nombre})"] = depto_obj
                if created:
                    self.stdout.write(f'  + Creado departamento: {depto_nombre} en {area_nombre}')
                else:
                    self.stdout.write(f'  ✓ Departamento existente: {depto_nombre} en {area_nombre}')

        self.stdout.write(self.style.SUCCESS(f'✓ Procesadas {len(areas)} áreas organizativas'))

        # Leer datos de mouse desde Excel
        maus_creados = 0
        errores = 0

        try:
            # Abrir el archivo Excel
            excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'maus.xlsx')
            wb = openpyxl.load_workbook(excel_path)
            ws = wb.active

            # Iterar sobre las filas del Excel (saltando el encabezado)
            for row in ws.iter_rows(min_row=2):
                try:
                    # Leer datos de cada columna según la estructura:
                    # 1. Unidad organizativa
                    # 2. Responsable del medio
                    # 3. Útil
                    # 4. Medio básico
                    # 5. (poner # inventario)
                    # 6. Situación actual
                    # 7. Si es de PI
                    ubicacion = row[0].value if row[0].value else ''
                    responsable_nombre = normalizar_nombre(row[1].value) if row[1].value else ''
                    util = bool(row[2].value == 1)  # True solo si es 1
                    medio_basico = bool(row[3].value == 1)  # True solo si es 1
                    maus_inv = row[4].value if row[4].value else ''
                    funciona = bool(row[5].value == 1)  # True solo si es 1
                    es_proyecto = bool(row[6].value == 1)  # True solo si es 1

                    if not ubicacion:  # Si no hay ubicación, saltamos esta fila
                        continue

                    # Obtener área
                    area_nombre_normalizado = mapeo_areas.get(ubicacion, ubicacion)
                    if area_nombre_normalizado not in areas:
                        self.stdout.write(self.style.WARNING(f'⚠ Área no encontrada: {ubicacion}'))
                        continue
                    area_obj = areas[area_nombre_normalizado]

                    # Obtener o crear responsable
                    responsable_obj = None
                    if responsable_nombre:
                        responsable_obj, created = Responsable.objects.get_or_create(
                            nombre__iexact=responsable_nombre,
                            defaults={'nombre': responsable_nombre, 'area': area_obj}
                        )
                        if created:
                            self.stdout.write(f'  + Creado responsable: {responsable_nombre}')
                        else:
                            if not responsable_obj.area:
                                responsable_obj.area = area_obj
                                responsable_obj.save()
                                self.stdout.write(f'  ✓ Actualizada área del responsable: {responsable_nombre} -> {area_obj}')
                            self.stdout.write(f'  ✓ Responsable existente: {responsable_nombre}')

                    # Crear o obtener número de inventario solo si existe en el Excel
                    num_inv = None
                    if maus_inv:
                        # Usar el código base sin modificar
                        base_codigo = str(maus_inv)
                        num_inv_obj, created = NumeroInventario.objects.get_or_create(
                            codigo=base_codigo,
                            tipo_dispositivo='Mouse'
                        )
                        if created:
                            self.stdout.write(f'  + Creado número de inventario: {base_codigo}')
                        else:
                            self.stdout.write(f'  ✓ Número de inventario existente: {base_codigo}')
                        num_inv = num_inv_obj

                    # Crear mouse
                    mouse = Mouse.objects.create(
                        numero_inventario=num_inv,
                        responsable=responsable_obj,
                        area=area_obj,
                        funciona=funciona,
                        es_proyecto_internacional=es_proyecto,
                        marca='Sin especificar'
                    )
                    
                    self.stdout.write(f'  + Creado mouse para {responsable_nombre} en {ubicacion} {f"con inventario {maus_inv}" if maus_inv else "sin número de inventario"}')
                    maus_creados += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error al procesar mouse: {e}'))
                    errores += 1
                    continue

            wb.close()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al abrir el archivo Excel: {e}'))
            return

        self.stdout.write(self.style.SUCCESS(f'✓ Creados {maus_creados} mouse'))
        if errores > 0:
            self.stdout.write(self.style.WARNING(f'⚠ Hubo {errores} errores durante la importación'))

        self.stdout.write(self.style.SUCCESS('Importación completada')) 