from django.core.management.base import BaseCommand
from ComponentesInternos.models import Procesador, RAM, DiscoDuro, SistemaOperativo

class Command(BaseCommand):
    help = 'Importa los datos iniciales de componentes (Procesadores, RAM, Discos Duros y Sistemas Operativos)'

    def handle(self, *args, **options):
        # Procesadores
        procesadores = [
            'celeron', 'Pentium III', 'Pentium IV', 'Dual Core', 'Core 2 Duo',
            'Core i3', 'Core i5', 'Core i7', 'Xeon', 'AMD', 'ATOM', 'Pentium Gold',
            'Pentium G2030'
        ]
        for proc in procesadores:
            Procesador.objects.get_or_create(nombre=proc)
            self.stdout.write(self.style.SUCCESS(f'Procesador creado: {proc}'))

        # RAM
        ram_capacidades = ['256 MB', '512MB', '1GB', '2GB', '4GB', '6GB', '8GB', '16GB']
        for ram in ram_capacidades:
            RAM.objects.get_or_create(capacidad=ram)
            self.stdout.write(self.style.SUCCESS(f'RAM creada: {ram}'))

        # Discos Duros
        hdd_capacidades = [
            '128GB', '160GB', '200GB', '256GB', '480GB', '512GB', '580GB', '1TB', '2TB'
        ]
        for hdd in hdd_capacidades:
            DiscoDuro.objects.get_or_create(capacidad=hdd)
            self.stdout.write(self.style.SUCCESS(f'Disco Duro creado: {hdd}'))

        # Sistemas Operativos
        sistemas = ['W7', 'W8', 'W8.1', 'W10', 'W11']
        for so in sistemas:
            SistemaOperativo.objects.get_or_create(nombre=so)
            self.stdout.write(self.style.SUCCESS(f'Sistema Operativo creado: {so}'))

        self.stdout.write(self.style.SUCCESS('Importación completada con éxito')) 