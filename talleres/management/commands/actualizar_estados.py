from django.core.management.base import BaseCommand
from django.utils import timezone
from talleres.models import Taller

class Command(BaseCommand):
    help = 'Actualiza automáticamente el estado de los talleres según sus fechas'

    def handle(self, *args, **options):
        """
        Actualiza el estado de los talleres según sus fechas:
        - PROGRAMADO: si la fecha de inicio es futura
        - EN_CURSO: si la fecha actual está entre la fecha de inicio y fin
        - FINALIZADO: si la fecha actual es posterior a la fecha de fin
        - No modifica los talleres CANCELADOS
        """
        # Obtener fecha actual
        hoy = timezone.now().date()
        
        # Obtener todos los talleres
        talleres = Taller.objects.exclude(estado='CANCELADO')
        
        talleres_actualizados = 0
        
        # Verificar y actualizar el estado de cada taller
        for taller in talleres:
            nuevo_estado = None
            
            # Determinar el nuevo estado basado en las fechas
            if hoy < taller.fecha_inicio:
                nuevo_estado = 'PROGRAMADO'
            elif hoy <= taller.fecha_fin:
                nuevo_estado = 'EN_CURSO'
            else:
                nuevo_estado = 'FINALIZADO'
            
            # Actualizar el estado si ha cambiado
            if taller.estado != nuevo_estado:
                self.stdout.write(f'Taller "{taller.nombre}": {taller.estado} -> {nuevo_estado}')
                taller.estado = nuevo_estado
                taller.save(update_fields=['estado'])
                talleres_actualizados += 1
        
        self.stdout.write(self.style.SUCCESS(f'Se actualizaron {talleres_actualizados} talleres'))
