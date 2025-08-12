from django.contrib import admin
from .models import Taller, Participante, Asistencia, Evaluacion, Material


class ParticipanteInline(admin.TabularInline):
    """
    Configuración para mostrar participantes como una tabla
    inline dentro del admin de talleres.
    """
    model = Participante
    extra = 0  # No mostrar campos extras vacíos
    readonly_fields = ['fecha_inscripcion']
    # Mostrar estos campos en la tabla
    fields = ['beneficiaria', 'nombres', 'apellidos', 'dni', 'estado', 'fecha_inscripcion']


class MaterialInline(admin.TabularInline):
    """
    Configuración para mostrar materiales como una tabla
    inline dentro del admin de talleres.
    """
    model = Material
    extra = 0  # No mostrar campos extras vacíos
    # Mostrar estos campos en la tabla
    fields = ['titulo', 'tipo', 'archivo', 'url']


@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Taller.
    """
    # Campos a mostrar en la lista de talleres
    list_display = ['nombre', 'fecha_inicio', 'fecha_fin', 'facilitador', 'estado', 'capacidad', 'inscritos_count']
    
    # Filtros laterales
    list_filter = ['estado', 'fecha_inicio']
    
    # Campos de búsqueda
    search_fields = ['nombre', 'descripcion', 'facilitador', 'lugar']
    
    # Ordenamiento predeterminado
    ordering = ['-fecha_inicio', 'nombre']
    
    # Campos agrupados en el formulario de edición
    fieldsets = [
        ('Información básica', {
            'fields': ['nombre', 'descripcion', 'estado']
        }),
        ('Programación', {
            'fields': ['fecha_inicio', 'fecha_fin', 'horario', 'lugar', 'capacidad']
        }),
        ('Responsables', {
            'fields': ['facilitador']
        }),
        ('Notas adicionales', {
            'fields': ['notas'],
            'classes': ['collapse']  # Sección colapsable
        }),
    ]
    
    # Incluir participantes y materiales como inlines
    inlines = [ParticipanteInline, MaterialInline]
    
    # Agregar campos calculados
    def inscritos_count(self, obj):
        """Calcular el número de participantes inscritos"""
        return obj.participante_set.count()
    inscritos_count.short_description = 'Inscritos'


@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Participante.
    """
    # Campos a mostrar en la lista de participantes
    list_display = ['nombre_completo', 'dni', 'taller', 'fecha_inscripcion', 'estado']
    
    # Filtros laterales
    list_filter = ['estado', 'fecha_inscripcion', 'taller']
    
    # Campos de búsqueda
    search_fields = ['nombres', 'apellidos', 'dni', 'beneficiaria__nombres', 'beneficiaria__apellidos']
    
    # Ordenamiento predeterminado
    ordering = ['-fecha_inscripcion']
    
    # Campos agrupados en el formulario de edición
    fieldsets = [
        ('Taller', {
            'fields': ['taller']
        }),
        ('Beneficiaria existente', {
            'fields': ['beneficiaria']
        }),
        ('Datos personales', {
            'fields': ['nombres', 'apellidos', 'dni', 'telefono', 'email']
        }),
        ('Estado de inscripción', {
            'fields': ['estado', 'fecha_inscripcion']
        }),
        ('Notas adicionales', {
            'fields': ['notas'],
            'classes': ['collapse']  # Sección colapsable
        }),
    ]
    
    # Campos de solo lectura
    readonly_fields = ['fecha_inscripcion']


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Asistencia.
    """
    # Campos a mostrar en la lista de asistencias
    list_display = ['participante', 'taller_nombre', 'fecha', 'estado', 'registrado_por']
    
    # Filtros laterales
    list_filter = ['estado', 'fecha', 'participante__taller']
    
    # Campos de búsqueda
    search_fields = ['participante__nombres', 'participante__apellidos', 'participante__dni', 'participante__beneficiaria__nombres']
    
    # Ordenamiento predeterminado
    ordering = ['-fecha', 'participante']
    
    # Campos de solo lectura
    readonly_fields = ['fecha_registro']
    
    def taller_nombre(self, obj):
        """Método para mostrar el nombre del taller en la lista"""
        return obj.participante.taller.nombre
    taller_nombre.short_description = 'Taller'


@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Evaluacion.
    """
    # Campos a mostrar en la lista de evaluaciones
    list_display = ['titulo', 'participante', 'taller_nombre', 'fecha', 'calificacion', 'nivel_logro']
    
    # Filtros laterales
    list_filter = ['nivel_logro', 'fecha', 'participante__taller']
    
    # Campos de búsqueda
    search_fields = ['titulo', 'participante__nombres', 'participante__apellidos', 'evaluador']
    
    # Ordenamiento predeterminado
    ordering = ['-fecha', 'participante']
    
    # Campos de solo lectura
    readonly_fields = ['fecha_registro']
    
    def taller_nombre(self, obj):
        """Método para mostrar el nombre del taller en la lista"""
        return obj.participante.taller.nombre
    taller_nombre.short_description = 'Taller'


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Material.
    """
    # Campos a mostrar en la lista de materiales
    list_display = ['titulo', 'taller', 'tipo', 'tiene_archivo', 'tiene_url', 'fecha_creacion']
    
    # Filtros laterales
    list_filter = ['tipo', 'taller']
    
    # Campos de búsqueda
    search_fields = ['titulo', 'descripcion', 'taller__nombre', 'autor']
    
    # Ordenamiento predeterminado
    ordering = ['-fecha_creacion']
    
    # Campos de solo lectura
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def tiene_archivo(self, obj):
        """Método para indicar si el material tiene archivo adjunto"""
        return bool(obj.archivo)
    tiene_archivo.boolean = True
    tiene_archivo.short_description = 'Archivo'
    
    def tiene_url(self, obj):
        """Método para indicar si el material tiene URL externa"""
        return bool(obj.url)
    tiene_url.boolean = True
    tiene_url.short_description = 'URL'
