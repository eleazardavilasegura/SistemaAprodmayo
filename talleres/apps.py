from django.apps import AppConfig


class TalleresConfig(AppConfig):
    """
    Configuración de la aplicación Talleres.
    
    Esta clase define la configuración básica de la aplicación 'talleres',
    incluyendo el nombre predeterminado y etiquetas para el panel de administración.
    """
    # Nombre corto de la aplicación
    name = 'talleres'
    
    # Nombre legible para humanos que aparecerá en el admin
    verbose_name = 'Gestión de Talleres'
