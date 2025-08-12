import os
import sys
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aprodmayo.settings")
django.setup()

# Importar modelos después de configurar Django
from talleres.models import Taller
from django.utils import timezone

def actualizar_estados():
    print('Actualizando estados de talleres:')
    
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
            print(f'- Taller {t.id}: {t.nombre} -> {t.get_estado_display()} (antes: {estado_anterior})')
        else:
            print(f'- Taller {t.id}: {t.nombre} mantiene estado {t.get_estado_display()}')

if __name__ == "__main__":
    actualizar_estados()
