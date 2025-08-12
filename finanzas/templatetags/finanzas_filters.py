"""
Filtros personalizados para formateo de valores monetarios y fechas
en el módulo de finanzas.
"""

from django import template
from django.utils.numberformat import format
import datetime

register = template.Library()

@register.filter(name='money_format')
def money_format(value):
    """
    Formatea un valor numérico como moneda (S/. XX,XXX.XX)
    
    Args:
        value: El valor numérico a formatear
        
    Returns:
        Cadena formateada como moneda peruana (S/.)
    """
    if value is None:
        return "S/. 0.00"
    
    formatted_value = format(
        value, 
        decimal_sep='.', 
        thousand_sep=',', 
        grouping=3, 
        force_grouping=True
    )
    return f"S/. {formatted_value}"
    
@register.filter(name='positive_class')
def positive_class(value):
    """
    Retorna una clase CSS basada en si el valor es positivo o negativo
    
    Args:
        value: El valor numérico
        
    Returns:
        String con la clase CSS correspondiente
    """
    if value is None:
        return ""
    
    if float(value) >= 0:
        return "text-success"
    else:
        return "text-danger"

@register.filter(name='get_range')
def get_range(value):
    """
    Retorna un rango de números para iterar.
    
    Args:
        value: El número máximo del rango
        
    Returns:
        Rango de números desde 0 hasta value-1
    """
    return range(value)

@register.filter(name='get_item')
def get_item(list_obj, index):
    """
    Obtiene un elemento específico de una lista por índice.
    
    Args:
        list_obj: La lista
        index: El índice del elemento a obtener
        
    Returns:
        El elemento en la posición index de la lista
    """
    try:
        return list_obj[int(index)]
    except (IndexError, TypeError, ValueError):
        return None

@register.filter(name='percentage')
def percentage(value, total):
    """
    Calcula el porcentaje de un valor con respecto a un total.
    
    Args:
        value: El valor para el cual calcular el porcentaje
        total: El valor total (100%)
        
    Returns:
        El porcentaje redondeado a dos decimales
    """
    try:
        return round((float(value) / float(total)) * 100, 2)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0

@register.filter(name='subtract')
def subtract(value, arg):
    """
    Resta dos números.
    
    Args:
        value: Minuendo
        arg: Sustraendo
        
    Returns:
        La diferencia entre value y arg
    """
    try:
        return float(value) - float(arg)
    except (TypeError, ValueError):
        return 0

@register.filter(name='divide')
def divide(value, arg):
    """
    Divide un número por otro.
    
    Args:
        value: Dividendo
        arg: Divisor
        
    Returns:
        El resultado de la división value/arg
    """
    try:
        return float(value) / float(arg)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0

@register.filter(name='add_days')
def add_days(date_str, days):
    """
    Agrega un número de días a una fecha en formato string.
    
    Args:
        date_str: Fecha en formato string (dd/mm/yyyy) o objeto date
        days: Número de días a agregar
    
    Returns:
        String con la fecha resultante en formato dd/mm/yyyy
    """
    try:
        if isinstance(date_str, str):
            date = datetime.datetime.strptime(date_str, '%d/%m/%Y').date()
        else:
            # Si ya es un objeto date
            date = date_str
            
        new_date = date + datetime.timedelta(days=int(days))
        return new_date.strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        return date_str
        
@register.filter(name='nombre_mes')
def nombre_mes(numero_mes):
    """
    Convierte el número de mes (01-12) a su nombre en español.
    
    Args:
        numero_mes: Número del mes como string ('01' a '12') o int (1 a 12)
        
    Returns:
        Nombre del mes en español
    """
    try:
        if isinstance(numero_mes, str):
            mes = int(numero_mes)
        else:
            mes = numero_mes
            
        nombres_meses = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        
        return nombres_meses[mes - 1]
    except (ValueError, TypeError, IndexError):
        return str(numero_mes)
