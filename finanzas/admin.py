"""
Configuración administrativa para el módulo de finanzas.
"""

from django.contrib import admin
from .models import Categoria, Socio, PagoSocio, Ingreso, Egreso, InformeFinanciero


class PagoSocioInline(admin.TabularInline):
    """Muestra los pagos asociados a un socio en la vista de admin"""
    model = PagoSocio
    extra = 0
    fields = ['fecha', 'monto', 'periodo_correspondiente', 'comprobante', 'observaciones']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Configuración de admin para las categorías financieras"""
    list_display = ['nombre', 'tipo', 'activo', 'descripcion']
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']


@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    """Configuración de admin para los socios"""
    list_display = ['nombres', 'apellidos', 'documento_identidad', 'telefono', 'estado', 'cuota_mensual']
    list_filter = ['estado', 'fecha_registro']
    search_fields = ['nombres', 'apellidos', 'documento_identidad', 'telefono']
    date_hierarchy = 'fecha_registro'
    inlines = [PagoSocioInline]
    
    fieldsets = (
        ('Información personal', {
            'fields': ('nombres', 'apellidos', 'documento_identidad', 'fecha_registro')
        }),
        ('Contacto', {
            'fields': ('telefono', 'correo', 'direccion')
        }),
        ('Estado y cuota', {
            'fields': ('estado', 'cuota_mensual', 'observaciones')
        }),
    )


@admin.register(PagoSocio)
class PagoSocioAdmin(admin.ModelAdmin):
    """Configuración de admin para pagos de socios"""
    list_display = ['socio', 'fecha', 'monto', 'periodo_correspondiente', 'metodo_pago', 'comprobante']
    list_filter = ['fecha', 'metodo_pago']
    search_fields = ['socio__nombres', 'socio__apellidos', 'periodo_correspondiente', 'comprobante']
    date_hierarchy = 'fecha'
    autocomplete_fields = ['socio']


@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    """Configuración de admin para ingresos"""
    list_display = ['fecha', 'categoria', 'descripcion', 'monto', 'metodo_ingreso', 'comprobante']
    list_filter = ['fecha', 'categoria', 'metodo_ingreso']
    search_fields = ['descripcion', 'comprobante', 'observaciones']
    date_hierarchy = 'fecha'


@admin.register(Egreso)
class EgresoAdmin(admin.ModelAdmin):
    """Configuración de admin para egresos"""
    list_display = ['fecha', 'categoria', 'descripcion', 'monto', 'metodo_pago', 'comprobante', 'proveedor']
    list_filter = ['fecha', 'categoria', 'metodo_pago']
    search_fields = ['descripcion', 'comprobante', 'proveedor', 'observaciones']
    date_hierarchy = 'fecha'


@admin.register(InformeFinanciero)
class InformeFinancieroAdmin(admin.ModelAdmin):
    """Configuración de admin para informes financieros"""
    list_display = ['titulo', 'fecha_inicio', 'fecha_fin', 'total_ingresos', 'total_egresos', 'saldo']
    list_filter = ['tipo_periodo', 'fecha_creacion']
    search_fields = ['titulo', 'observaciones', 'creado_por']
    date_hierarchy = 'fecha_fin'
    
    readonly_fields = ['total_ingresos', 'total_egresos', 'saldo', 'fecha_creacion']
    
    fieldsets = (
        ('Información general', {
            'fields': ('titulo', 'fecha_inicio', 'fecha_fin', 'tipo_periodo')
        }),
        ('Resultados', {
            'fields': ('total_ingresos', 'total_egresos', 'saldo')
        }),
        ('Notas adicionales', {
            'fields': ('observaciones', 'creado_por', 'fecha_creacion')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Genera automáticamente los cálculos al guardar el informe"""
        super().save_model(request, obj, form, change)
        obj.generar_informe()
