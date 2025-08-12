from django.core.management.base import BaseCommand
from django.utils import timezone
from talleres.models import Taller

class Command(BaseCommand):
    help = 'Actualiza los estados de los talleres basado en las fechas actuales'

    def handle(self, *args, **kwargs):
        self.stdout.write('Actualizando estados de talleres:')
        
        actualizados = 0
        sin_cambios = 0
        
        for t in Taller.objects.all():
            estado_anterior = t.estado
            today = timezone.now().date()
            
            if today < t.fecha_inicio:
                t.estado = 'PROGRAMADO'
            elif t.fecha_inicio <= today <= t.fecha_fin:
                t.estado = 'EN_CURSO'
            else:
                t.estado = 'FINALIZADO'
            
            # Solo guardar si ha cambiado el estado
            if t.estado != estado_anterior:
                t.save()
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Taller {t.id}: {t.nombre} -> {t.get_estado_display()} (antes: {dict(Taller.ESTADO_CHOICES).get(estado_anterior)})'
                ))
                actualizados += 1
            else:
                self.stdout.write(self.style.WARNING(
                    f'- Taller {t.id}: {t.nombre} mantiene estado {t.get_estado_display()}'
                ))
                sin_cambios += 1
        
        self.stdout.write(self.style.SUCCESS(f'\nProceso completado: {actualizados} talleres actualizados, {sin_cambios} sin cambios'))
