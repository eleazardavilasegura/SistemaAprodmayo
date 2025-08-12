"""
Este archivo contiene filtros personalizados para trabajar con campos de formularios Django.
"""

from django import template
from django.forms.widgets import Input, Textarea, Select, CheckboxInput
from django.utils.html import format_html

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Agrega una clase CSS a un widget de formulario Django.
    
    Soporta diferentes tipos de campos de formulario y es más robusto
    que la versión anterior.
    
    Args:
        field: El campo del formulario
        css_class: La clase CSS a agregar
        
    Returns:
        El widget con la clase CSS añadida
    """
    if field is None:
        return ''
    
    # Para campos de formulario Django
    if hasattr(field, 'field') and hasattr(field.field, 'widget'):
        attrs = field.field.widget.attrs.copy()
        css_classes = attrs.get('class', '')
        if css_classes:
            css_classes = f"{css_classes} {css_class}"
        else:
            css_classes = css_class
        attrs['class'] = css_classes
        return field.as_widget(attrs=attrs)
    
    # Para widgets directos
    elif hasattr(field, 'as_widget'):
        return field.as_widget(attrs={"class": css_class})
    
    # Para valores que no son campos de formulario
    return field
