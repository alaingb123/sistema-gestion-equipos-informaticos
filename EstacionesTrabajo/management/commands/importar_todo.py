from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Importa todos los datos (componentes, PCs, monitores, teclados, mouse, impresoras, escáneres y UPS)'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando importación masiva...\n')

        # Primero importar componentes
        try:
            self.stdout.write('\n📥 Importando Componentes...')
            call_command('importar_componentes')
            self.stdout.write(self.style.SUCCESS(f'✅ Componentes importados correctamente\n'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Error al importar componentes: {str(e)}\n'
                )
            )

        # Lista de comandos a ejecutar para dispositivos
        comandos = [
            ('importar_pcs_desde_excel', 'PCs'),
            ('importar_monitores', 'Monitores'),
            ('importar_teclados_desde_excel', 'Teclados'),
            ('importar_maus_desde_excel', 'Mouse'),
            ('importar_impresoras_desde_excel', 'Impresoras'),
            ('importar_scaners_desde_excel', 'Escáneres'),
            ('importar_ups_desde_excel', 'UPS'),
            ('asignar_sistemas', 'Sistemas Operativos'),
            ('asignar_procesadores', 'Procesadores')
        ]

        for comando, nombre in comandos:
            try:
                self.stdout.write(f'\n📥 Importando {nombre}...')
                call_command(comando)
                self.stdout.write(self.style.SUCCESS(f'✅ {nombre} importados correctamente\n'))
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error al importar {nombre}: {str(e)}\n'
                    )
                )

        self.stdout.write(self.style.SUCCESS('\n🎉 Proceso de importación masiva completado!')) 