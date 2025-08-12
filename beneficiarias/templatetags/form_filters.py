"""
Este archivo contiene filtros personalizados para las plantillas Django.
Los filtros son funciones que pueden ser usadas en las plantillas para 
transformar o procesar datos antes de mostrarlos.
"""

from django import template
from django.forms.widgets import Widget
from django.forms.boundfield import BoundField

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
    # Manejar el caso de BoundField (campos de formulario)
    if isinstance(value, BoundField):
        attrs = {}
        if value.field.widget.attrs:
            attrs = value.field.widget.attrs.copy()
        
        if 'class' in attrs:
            attrs['class'] = f"{attrs['class']} {css_class}"
        else:
            attrs['class'] = css_class
            
        return value.as_widget(attrs=attrs)
    
    # Manejar el caso de widgets directos
    elif hasattr(value, 'as_widget'):
        attrs = {}
        if hasattr(value, 'attrs'):
            attrs = value.attrs.copy()
            
        if 'class' in attrs:
            attrs['class'] = f"{attrs['class']} {css_class}"
        else:
            attrs['class'] = css_class
            
        return value.as_widget(attrs=attrs)
    
    # Si no es ni un BoundField ni un widget, devolvemos el valor sin modificar
    return value
