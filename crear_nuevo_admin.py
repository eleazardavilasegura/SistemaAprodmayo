"""
Script para crear un nuevo superusuario con nombre diferente.
"""

import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aprodmayo.settings')
django.setup()

# Importar modelo de Usuario
from django.contrib.auth import get_user_model
Usuario = get_user_model()

# Crear nuevo usuario
try:
    nuevo_usuario = Usuario.objects.create_superuser(
        username='administrador',
        password='admin123',
        email='administrador@aprodmayo.org',
        first_name='Administrador',
        last_name='Principal',
        role='administrador',
        telefono='123456789',
        permiso_beneficiarias=True,
        permiso_finanzas=True,
        permiso_talleres=True,
        permiso_reportes=True
    )
    print("¡Usuario creado con éxito!")
    print("Usuario: administrador")
    print("Contraseña: admin123")
except Exception as e:
    print(f"Error: {e}")
