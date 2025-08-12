"""
Filtros personalizados para el módulo de talleres.
"""

from django import template

register = template.Library()

@register.filter(name='default_if_none')
def default_if_none(value, default=0):
    """
    Retorna el valor por defecto si el valor original es None.
    
    Args:
        value: El valor a verificar
        default: El valor por defecto
        
    Returns:
        El valor original si no es None, o el valor por defecto
    """
    return value if value is not None else default
