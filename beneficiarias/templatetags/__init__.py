"""
Este archivo contiene filtros personalizados para las plantillas Django.
Los filtros son funciones que pueden ser usadas en las plantillas para 
transformar o procesar datos antes de mostrarlos.
"""

from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    """
    Agrega una clase CSS a un widget de formulario Django.
    
    Args:
        value: El campo del formulario (widget)
        css_class: La clase CSS a agregar
        
    Returns:
        El widget con la clase CSS añadida
    """
    return value.as_widget(attrs={"class": css_class})
