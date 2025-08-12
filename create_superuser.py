"""
Script para crear un superusuario de Django.
Ejecutar con:
python create_superuser.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aprodmayo.settings')
django.setup()

from usuarios.models import Usuario

# Verificar si el usuario ya existe
if not Usuario.objects.filter(username='admin').exists():
    usuario = Usuario.objects.create_superuser(
        username='admin',
        password='admin123',
        email='admin@aprodmayo.org',
        first_name='Administrador',
        last_name='Sistema',
        role='administrador',
        telefono='123456789',
        permiso_beneficiarias=True,
        permiso_finanzas=True,
        permiso_talleres=True,
        permiso_reportes=True
    )
    print(f'Superusuario {usuario.username} creado exitosamente.')
else:
    # Actualizar la contraseña del usuario existente
    usuario = Usuario.objects.get(username='admin')
    usuario.set_password('admin123')
    usuario.save()
    print(f'Contraseña actualizada para el usuario {usuario.username}.')

print("Usuario: admin")
print("Contraseña: admin123")
