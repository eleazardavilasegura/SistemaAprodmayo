"""
Script para cambiar la contraseña del usuario administrador.
Este script es muy simple y directo.
"""

import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aprodmayo.settings')
django.setup()

# Importar modelo de Usuario
from django.contrib.auth import get_user_model
Usuario = get_user_model()

# Buscar usuario admin
try:
    admin = Usuario.objects.get(username='admin')
    # Cambiar contraseña
    admin.set_password('admin123')
    admin.save()
    print("¡Contraseña actualizada con éxito!")
    print("Usuario: admin")
    print("Contraseña: admin123")
except Exception as e:
    print(f"Error: {e}")
