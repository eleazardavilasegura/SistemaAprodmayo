from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    """
    Agrega una clase CSS a un campo de formulario.
    
    Uso:
        {{ form.field|add_class:"form-control" }}
    """
    if field:
        current_classes = field.field.widget.attrs.get('class', '')
        if current_classes:
            # Si ya hay clases, añadimos la nueva clase
            field.field.widget.attrs['class'] = f"{current_classes} {css_class}"
        else:
            # Si no hay clases, establecemos la clase
            field.field.widget.attrs['class'] = css_class
    return field

@register.filter
def add_error_class(field, css_class):
    """
    Agrega una clase CSS de error a un campo de formulario si contiene errores.
    
    Uso:
        {{ form.field|add_error_class:"is-invalid" }}
    """
    if field and hasattr(field, 'errors') and field.errors:
        current_classes = field.field.widget.attrs.get('class', '')
        if current_classes:
            # Si ya hay clases, añadimos la nueva clase de error
            if css_class not in current_classes:
                field.field.widget.attrs['class'] = f"{current_classes} {css_class}"
        else:
            # Si no hay clases, establecemos la clase de error
            field.field.widget.attrs['class'] = css_class
    return field

@register.filter
def placeholder(field, text):
    """
    Agrega un placeholder a un campo de formulario.
    
    Uso:
        # Definición de filtros personalizados para formularios en finanzas
from django import template
from django.forms.boundfield import BoundField

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    # Agrega clase CSS a un campo de formulario
    if field is None:
        return ''
    
    if isinstance(field, BoundField):
        return field.as_widget(attrs={
            'class': f"{field.field.widget.attrs.get('class', '')} {css_class}".strip()
        })
    return field

@register.filter(name='add_error_class')
def add_error_class(field, css_class):
    # Agrega clase CSS de error si el campo tiene errores
    if field is None:
        return ''
    
    if isinstance(field, BoundField) and field.errors:
        return field.as_widget(attrs={
            'class': f"{field.field.widget.attrs.get('class', '')} {css_class}".strip()
        })
    return field

@register.filter(name='placeholder')
def placeholder(field, text):
    # Agrega placeholder a un campo de formulario
    if isinstance(field, BoundField):
        return field.as_widget(attrs={
            'placeholder': text,
            **field.field.widget.attrs
        })
    return field
    """
    return field.as_widget(attrs={"placeholder": text})
