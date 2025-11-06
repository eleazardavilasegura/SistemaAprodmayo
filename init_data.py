#!/usr/bin/env python
"""
Script para inicializar datos básicos del sistema APRODMAYO
Ejecutar con: python init_data.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aprodmayo.settings')
django.setup()

from django.contrib.auth import get_user_model
from finanzas.models import Categoria
from usuarios.models import Usuario

def crear_categorias_basicas():
    """Crear categorías básicas para el sistema financiero"""
    categorias_ingreso = [
        ('Cuotas de Socios', 'Pagos mensuales de socios'),
        ('Donaciones', 'Donaciones recibidas de terceros'),
        ('Subvenciones', 'Apoyo gubernamental o de ONG'),
        ('Eventos', 'Ingresos por eventos organizados'),
        ('Otros Ingresos', 'Otros tipos de ingresos'),
    ]
    
    categorias_egreso = [
        ('Servicios Básicos', 'Luz, agua, teléfono, internet'),
        ('Material de Oficina', 'Papelería, útiles de oficina'),
        ('Talleres y Capacitación', 'Gastos en talleres y capacitaciones'),
        ('Transporte', 'Gastos de transporte y movilidad'),
        ('Alimentación', 'Gastos en alimentación para eventos'),
        ('Otros Gastos', 'Otros tipos de gastos'),
    ]
    
    print("Creando categorías de ingresos...")
    for nombre, descripcion in categorias_ingreso:
        categoria, created = Categoria.objects.get_or_create(
            nombre=nombre,
            tipo='INGRESO',
            defaults={'descripcion': descripcion, 'activo': True}
        )
        if created:
            print(f"  ✓ Creada: {nombre}")
        else:
            print(f"  - Ya existe: {nombre}")
    
    print("Creando categorías de egresos...")
    for nombre, descripcion in categorias_egreso:
        categoria, created = Categoria.objects.get_or_create(
            nombre=nombre,
            tipo='EGRESO',
            defaults={'descripcion': descripcion, 'activo': True}
        )
        if created:
            print(f"  ✓ Creada: {nombre}")
        else:
            print(f"  - Ya existe: {nombre}")

def crear_usuario_admin():
    """Crear usuario administrador por defecto"""
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@aprodmayo.org',
            password='admin123',  # Cambiar en producción
            first_name='Administrador',
            last_name='Sistema',
            role=Usuario.ADMINISTRADOR,
            permiso_beneficiarias=True,
            permiso_finanzas=True,
            permiso_talleres=True,
            permiso_reportes=True,
            is_staff=True,
            is_superuser=True
        )
        print("✓ Usuario administrador creado (admin/admin123)")
    else:
        print("- Usuario administrador ya existe")

def main():
    print("=" * 50)
    print("INICIALIZANDO DATOS BÁSICOS DE APRODMAYO")
    print("=" * 50)
    
    try:
        crear_categorias_basicas()
        print()
        crear_usuario_admin()
        print()
        print("✅ Inicialización completada exitosamente")
        print()
        print("IMPORTANTE:")
        print("- Cambie la contraseña del administrador (admin/admin123)")
        print("- Configure las variables de entorno apropiadas")
        print("- Ejecute las migraciones: python manage.py migrate")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()