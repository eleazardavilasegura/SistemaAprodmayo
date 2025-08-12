"""
Filtros personalizados para formularios y plantillas en todo el proyecto APRODMAYO.
Este archivo contiene filtros que pueden ser usados en cualquier aplicación del proyecto.
"""

from django import template
from django.forms.boundfield import BoundField

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Agrega una clase CSS a un campo de formulario Django.
    Compatible con BoundField y widgets directos.
    
    Args:
        field: El campo del formulario
        css_class: La clase CSS a agregar
        
    Returns:
        El campo con la clase CSS añadida
    """
    if field is None:
        return ''
    
    # Si es un BoundField (lo más común)
    if isinstance(field, BoundField):
        return field.as_widget(attrs={
            'class': f"{field.field.widget.attrs.get('class', '')} {css_class}".strip()
        })
    
    # Si es un widget directo
    if hasattr(field, 'as_widget'):
        attrs = {}
        if hasattr(field, 'attrs'):
            attrs = field.attrs.copy()
        
        if 'class' in attrs:
            attrs['class'] = f"{attrs['class']} {css_class}"
        else:
            attrs['class'] = css_class
            
        return field.as_widget(attrs=attrs)
    
    # Para cualquier otro caso
    return field

@register.filter(name='add_error_class')
def add_error_class(field, css_class):
    """
    Agrega una clase CSS a un campo si contiene errores.
    
    Args:
        field: El campo del formulario
        css_class: La clase CSS a agregar si hay errores
        
    Returns:
        El campo con la clase CSS añadida si hay errores
    """
    if field is None:
        return ''
    
    if isinstance(field, BoundField) and field.errors:
        return field.as_widget(attrs={
            'class': f"{field.field.widget.attrs.get('class', '')} {css_class}".strip()
        })
    
    return field

@register.filter(name='field_type')
def field_type(field):
    """
    Retorna el tipo de campo de un BoundField.
    
    Args:
        field: El campo del formulario
        
    Returns:
        String con el nombre del tipo de widget
    """
    if isinstance(field, BoundField):
        return field.field.widget.__class__.__name__
    return ''

@register.filter(name='placeholder')
def placeholder(field, text):
    """
    Agrega un placeholder a un campo de formulario.
    
    Args:
        field: El campo del formulario
        text: El texto a usar como placeholder
        
    Returns:
        El campo con el placeholder añadido
    """
    if isinstance(field, BoundField):
        return field.as_widget(attrs={
            'placeholder': text,
            **field.field.widget.attrs
        })
    return field
