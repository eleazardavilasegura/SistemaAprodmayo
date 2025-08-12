from django.db import models
from django.utils import timezone


class Beneficiaria(models.Model):
    """Modelo para registrar los datos de una persona maltratada"""
    # Información de recepción
    fecha_ingreso = models.DateField(default=timezone.now)
    hora_ingreso = models.TimeField(default=timezone.now)
    
    # Información personal
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    edad = models.PositiveIntegerField(null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    documento_identidad = models.CharField(max_length=20, blank=True)
    tipo_documento = models.CharField(max_length=20, choices=[
        ('DNI', 'DNI'),
        ('PASAPORTE', 'Pasaporte'),
        ('CARNET_EXTRANJERIA', 'Carnet de Extranjería'),
        ('OTRO', 'Otro'),
    ], default='DNI')
    
    # Contacto
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    
    # Estado civil
    estado_civil = models.CharField(max_length=20, choices=[
        ('SOLTERA', 'Soltera'),
        ('CASADA', 'Casada'),
        ('CONVIVIENTE', 'Conviviente'),
        ('DIVORCIADA', 'Divorciada'),
        ('VIUDA', 'Viuda'),
    ], blank=True)
    
    # Educación
    nivel_educativo = models.CharField(max_length=50, choices=[
        ('SIN_ESTUDIOS', 'Sin estudios'),
        ('PRIMARIA_INCOMPLETA', 'Primaria incompleta'),
        ('PRIMARIA_COMPLETA', 'Primaria completa'),
        ('SECUNDARIA_INCOMPLETA', 'Secundaria incompleta'),
        ('SECUNDARIA_COMPLETA', 'Secundaria completa'),
        ('TECNICO_INCOMPLETO', 'Técnico incompleto'),
        ('TECNICO_COMPLETO', 'Técnico completo'),
        ('UNIVERSITARIO_INCOMPLETO', 'Universitario incompleto'),
        ('UNIVERSITARIO_COMPLETO', 'Universitario completo'),
    ], blank=True)
    
    # Situación laboral
    ocupacion = models.CharField(max_length=100, blank=True)
    situacion_laboral = models.CharField(max_length=50, choices=[
        ('EMPLEADA', 'Empleada'),
        ('DESEMPLEADA', 'Desempleada'),
        ('TRABAJADORA_INDEPENDIENTE', 'Trabajadora independiente'),
        ('AMA_DE_CASA', 'Ama de casa'),
        ('ESTUDIANTE', 'Estudiante'),
        ('JUBILADA', 'Jubilada'),
        ('OTRA', 'Otra'),
    ], blank=True)
    
    # Información sobre el caso
    motivo_consulta = models.TextField(blank=True)
    tipo_violencia = models.CharField(max_length=50, choices=[
        ('FISICA', 'Física'),
        ('PSICOLOGICA', 'Psicológica'),
        ('SEXUAL', 'Sexual'),
        ('ECONOMICA', 'Económica'),
        ('PATRIMONIAL', 'Patrimonial'),
        ('OTRAS', 'Otras'),
    ], blank=True)
    descripcion_situacion = models.TextField(blank=True)
    
    # Información médica
    problemas_salud = models.TextField(blank=True)
    medicacion = models.TextField(blank=True)
    
    # Información de hijos
    tiene_hijos = models.BooleanField(default=False)
    numero_hijos = models.PositiveIntegerField(default=0)
    
    # Información de la vivienda
    situacion_vivienda = models.CharField(max_length=50, choices=[
        ('PROPIA', 'Propia'),
        ('ALQUILADA', 'Alquilada'),
        ('FAMILIAR', 'Familiar'),
        ('OTRO', 'Otro'),
    ], blank=True)
    
    # Seguimiento
    seguimiento_requerido = models.BooleanField(default=False)
    notas_seguimiento = models.TextField(blank=True)
    
    # Persona que recibe el caso
    recibido_por = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    class Meta:
        verbose_name = "Beneficiaria"
        verbose_name_plural = "Beneficiarias"


class Acompanante(models.Model):
    """Modelo para registrar los datos de acompañantes"""
    beneficiaria = models.ForeignKey(
        Beneficiaria, 
        on_delete=models.CASCADE,
        related_name='acompanantes'
    )
    
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    parentesco = models.CharField(max_length=50, choices=[
        ('CONYUGE', 'Cónyuge/Pareja'),
        ('HIJO_A', 'Hijo/a'),
        ('PADRE_MADRE', 'Padre/Madre'),
        ('HERMANO_A', 'Hermano/a'),
        ('OTRO_FAMILIAR', 'Otro familiar'),
        ('AMIGO_A', 'Amigo/a'),
        ('PROFESIONAL', 'Profesional'),
        ('OTRO', 'Otro'),
    ])
    edad = models.PositiveIntegerField(null=True, blank=True)
    documento_identidad = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.get_parentesco_display()})"
    
    class Meta:
        verbose_name = "Acompañante"
        verbose_name_plural = "Acompañantes"


class Hijo(models.Model):
    """Modelo para registrar los datos de los hijos de la beneficiaria"""
    beneficiaria = models.ForeignKey(
        Beneficiaria, 
        on_delete=models.CASCADE,
        related_name='hijos'
    )
    
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    edad = models.PositiveIntegerField(null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=10, choices=[
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('OTRO', 'Otro'),
    ])
    escolaridad = models.CharField(max_length=50, blank=True)
    vive_con_beneficiaria = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    class Meta:
        verbose_name = "Hijo"
        verbose_name_plural = "Hijos"


class SeguimientoCaso(models.Model):
    """Modelo para registrar el seguimiento de cada caso"""
    beneficiaria = models.ForeignKey(
        Beneficiaria, 
        on_delete=models.CASCADE,
        related_name='seguimientos'
    )
    
    fecha = models.DateField(default=timezone.now)
    tipo_atencion = models.CharField(max_length=50, choices=[
        ('PSICOLOGICA', 'Atención psicológica'),
        ('LEGAL', 'Atención legal'),
        ('SOCIAL', 'Atención social'),
        ('MEDICA', 'Atención médica'),
        ('OTRA', 'Otra'),
    ])
    profesional = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField()
    acuerdos = models.TextField(blank=True)
    proxima_cita = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Seguimiento {self.fecha} - {self.beneficiaria}"
    
    class Meta:
        verbose_name = "Seguimiento de Caso"
        verbose_name_plural = "Seguimientos de Casos"
