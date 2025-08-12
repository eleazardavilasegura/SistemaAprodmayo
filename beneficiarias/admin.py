from django.contrib import admin
from .models import Beneficiaria, Acompanante, Hijo, SeguimientoCaso


class AcompananteInline(admin.TabularInline):
    model = Acompanante
    extra = 1


class HijoInline(admin.TabularInline):
    model = Hijo
    extra = 1


class SeguimientoCasoInline(admin.TabularInline):
    model = SeguimientoCaso
    extra = 1


@admin.register(Beneficiaria)
class BeneficiariaAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'documento_identidad', 'telefono', 'fecha_ingreso')
    list_filter = ('fecha_ingreso', 'tipo_violencia', 'seguimiento_requerido')
    search_fields = ('nombres', 'apellidos', 'documento_identidad', 'telefono')
    date_hierarchy = 'fecha_ingreso'
    fieldsets = (
        ('Información de recepción', {
            'fields': ('fecha_ingreso', 'hora_ingreso', 'recibido_por')
        }),
        ('Información personal', {
            'fields': ('nombres', 'apellidos', 'edad', 'fecha_nacimiento', 
                      'tipo_documento', 'documento_identidad', 'direccion',
                      'telefono', 'correo', 'estado_civil')
        }),
        ('Información socioeconómica', {
            'fields': ('nivel_educativo', 'ocupacion', 'situacion_laboral', 'situacion_vivienda')
        }),
        ('Información del caso', {
            'fields': ('motivo_consulta', 'tipo_violencia', 'descripcion_situacion')
        }),
        ('Información médica', {
            'fields': ('problemas_salud', 'medicacion')
        }),
        ('Información familiar', {
            'fields': ('tiene_hijos', 'numero_hijos')
        }),
        ('Seguimiento', {
            'fields': ('seguimiento_requerido', 'notas_seguimiento')
        })
    )
    inlines = [AcompananteInline, HijoInline, SeguimientoCasoInline]


@admin.register(Acompanante)
class AcompananteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'parentesco', 'beneficiaria')
    list_filter = ('parentesco',)
    search_fields = ('nombres', 'apellidos', 'documento_identidad', 
                    'beneficiaria__nombres', 'beneficiaria__apellidos')


@admin.register(Hijo)
class HijoAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'edad', 'genero', 'beneficiaria')
    list_filter = ('genero', 'vive_con_beneficiaria')
    search_fields = ('nombres', 'apellidos', 'beneficiaria__nombres', 'beneficiaria__apellidos')


@admin.register(SeguimientoCaso)
class SeguimientoCasoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo_atencion', 'profesional', 'beneficiaria', 'proxima_cita')
    list_filter = ('fecha', 'tipo_atencion')
    search_fields = ('profesional', 'descripcion', 'beneficiaria__nombres', 'beneficiaria__apellidos')
    date_hierarchy = 'fecha'
