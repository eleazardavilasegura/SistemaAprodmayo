# 🌟 Sistema APRODMAYO

Sistema integral de gestión para APRODMAYO (Asociación Protectora de los Derechos de la Mujer - Mayo), diseñado para apoyar a mujeres en situación de vulnerabilidad.

**Desarrollado por**: [Eleazar Davila Segura](https://github.com/eleazardavilasegura) 👨‍💻

---

## 👨‍💻 Acerca del Desarrollador

**Eleazar Davila Segura** es un desarrollador de software especializado en aplicaciones web con Django y Python. Este proyecto representa su compromiso con el desarrollo de soluciones tecnológicas que generen un impacto social positivo.

- 🚀 **Especialidades**: Python, Django, JavaScript, PostgreSQL
- 🌟 **Misión**: Crear tecnología que empodere a organizaciones sociales
- 📧 **Contacto**: eleazardavilasegura@gmail.com

---

## 📋 Características Principales

- **Gestión de Beneficiarias**: Registro y seguimiento de casos
- **Sistema Financiero**: Control de ingresos, egresos y socios
- **Gestión de Talleres**: Organización y seguimiento de talleres formativos
- **Sistema de Reportes**: Generación de informes en PDF y Excel
- **Control de Usuarios**: Sistema de roles y permisos
- **Interfaz Moderna**: Diseño responsivo con Bootstrap 5

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.8+
- PostgreSQL 12+
- pip (gestor de paquetes de Python)

### 1. Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd SistemaAprodmayo
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
cp .env.example .env
```
Editar el archivo `.env` con sus configuraciones específicas.

### 5. Configurar Base de Datos
```bash
# Crear base de datos PostgreSQL
createdb aprodmayo

# Ejecutar migraciones
python manage.py migrate
```

### 6. Inicializar Datos Básicos
```bash
python init_data.py
```

### 7. Crear Superusuario (Opcional)
```bash
python manage.py createsuperuser
```

### 8. Ejecutar el Servidor
```bash
python manage.py runserver
```

## 🔧 Configuración de Producción

### Variables de Entorno Importantes
```env
SECRET_KEY=su-clave-secreta-unica
DEBUG=False
ALLOWED_HOSTS=su-dominio.com,www.su-dominio.com
DB_NAME=aprodmayo_prod
DB_USER=usuario_db
DB_PASSWORD=contraseña_segura
DB_HOST=localhost
DB_PORT=5432
```

### Comandos para Producción
```bash
# Recopilar archivos estáticos
python manage.py collectstatic

# Crear usuario administrador
python manage.py createsuperuser

# Ejecutar con Gunicorn
gunicorn aprodmayo.wsgi:application
```

## 📊 Estructura del Proyecto

```
SistemaAprodmayo/
├── aprodmayo/              # Configuración principal
├── beneficiarias/          # Gestión de beneficiarias
├── finanzas/              # Sistema financiero
├── talleres/              # Gestión de talleres
├── reportes/              # Sistema de reportes
├── usuarios/              # Gestión de usuarios
├── templates/             # Plantillas HTML
├── static/               # Archivos estáticos
├── media/                # Archivos subidos
└── logs/                 # Archivos de log
```

## 👤 Usuarios y Permisos

### Roles Disponibles
- **Administrador**: Acceso completo al sistema
- **Empleado**: Acceso limitado según permisos asignados

### Permisos por Módulo
- Beneficiarias
- Finanzas
- Talleres
- Reportes

## 🔒 Seguridad

- Autenticación basada en sesiones Django
- Control de acceso por roles y permisos
- Validación CSRF habilitada
- Configuraciones de seguridad para producción
- Logs de actividad del sistema

## 📈 Reportes Disponibles

1. **Balance Financiero**: Ingresos vs Egresos
2. **Reporte de Beneficiarias**: Estadísticas y listados
3. **Reporte de Talleres**: Asistencia y evaluaciones

### Formatos de Exportación
- HTML (vista web)
- PDF (imprimible)
- Excel (análisis de datos)

## 🛠️ Scripts Útiles

### Resetear Contraseña de Usuario
```bash
python reset_password.py usuario@email.com
```

### Crear Nuevo Administrador
```bash
python crear_nuevo_admin.py
```

### Actualizar Estados
```bash
python actualizar_estados.py
```

## 🐛 Resolución de Problemas

### Error de Base de Datos
```bash
# Verificar conexión a PostgreSQL
python manage.py dbshell
```

### Error de Migraciones
```bash
# Revisar estado de migraciones
python manage.py showmigrations

# Aplicar migraciones específicas
python manage.py migrate app_name migration_name
```

### Error de Archivos Estáticos
```bash
# Recopilar archivos estáticos
python manage.py collectstatic --clear
```

## 📱 Tecnologías Utilizadas

- **Backend**: Django 5.2.5
- **Base de Datos**: PostgreSQL
- **Frontend**: Bootstrap 5, JavaScript
- **Reportes**: ReportLab, xhtml2pdf, xlsxwriter
- **Estilos**: CSS3, Animate.css
- **Iconos**: Bootstrap Icons

## 🤝 Contribuir

Si deseas contribuir al proyecto, por favor:

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

**Mantenedor**: Eleazar Davila Segura - Todas las contribuciones son bienvenidas.

## 📞 Soporte

Para soporte técnico, contactar a:
- **Desarrollador Principal**: Eleazar Davila Segura
- Email: eleazardavilasegura@gmail.com
- GitHub: [@eleazardavilasegura](https://github.com/eleazardavilasegura)
- LinkedIn: [Eleazar Davila Segura](https://www.linkedin.com/in/eleazardavilasegura)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

**Copyright © 2025 Eleazar Davila Segura**

## 🙏 Agradecimientos

- **Desarrollado por**: Eleazar Davila Segura
- A todo el equipo de APRODMAYO (Asociación Protectora de los Derechos de la Mujer - Mayo) por su confianza
- A las beneficiarias que inspiran este trabajo social
- A la comunidad de desarrolladores de Django
- A GitHub Copilot por la asistencia en el desarrollo
