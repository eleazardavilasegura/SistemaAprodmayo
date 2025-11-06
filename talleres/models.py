from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from beneficiarias.models import Beneficiaria
import uuid


def generar_codigo_certificado():
    """Genera un código único para certificados"""
    return f"APRO-{uuid.uuid4().hex[:8].upper()}"


class Taller(models.Model):
    """
    Modelo que representa un taller ofrecido por APRODMAYO.
    
    Almacena la información básica de los talleres que se imparten,
    como nombre, descripción, fechas de inicio y fin, y capacidad máxima.
    """
    
    # Nombre del taller
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre del taller",
        help_text="Nombre completo del taller"
    )
    
    # Descripción detallada del taller
    descripcion = models.TextField(
        verbose_name="Descripción",
        help_text="Descripción detallada del taller, objetivos y metodología"
    )
    
    # Fecha de inicio del taller
    fecha_inicio = models.DateField(
        verbose_name="Fecha de inicio",
        help_text="Fecha en que inicia el taller"
    )
    
    # Fecha de finalización del taller
    fecha_fin = models.DateField(
        verbose_name="Fecha de fin",
        help_text="Fecha en que finaliza el taller"
    )
    
    # Horario del taller
    horario = models.CharField(
        max_length=100,
        verbose_name="Horario",
        help_text="Horario del taller, por ejemplo: 'Lunes y Miércoles de 15:00 a 17:00'"
    )
    
    # Lugar donde se realiza el taller
    lugar = models.CharField(
        max_length=200,
        verbose_name="Lugar",
        help_text="Lugar donde se realiza el taller"
    )
    
    # Capacidad máxima de participantes
    capacidad = models.PositiveIntegerField(
        verbose_name="Capacidad máxima",
        help_text="Número máximo de participantes permitidos",
        validators=[MinValueValidator(1)]
    )
    
    # Facilitador o responsable del taller
    facilitador = models.CharField(
        max_length=200,
        verbose_name="Facilitador",
        help_text="Nombre del facilitador o responsable del taller"
    )
    
    # Estado del taller (programado, en curso, finalizado, cancelado)
    ESTADO_CHOICES = [
        ('PROGRAMADO', 'Programado'),
        ('EN_CURSO', 'En curso'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PROGRAMADO',
        verbose_name="Estado del taller"
    )
    
    # Notas adicionales sobre el taller
    notas = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas adicionales",
        help_text="Información adicional o requisitos especiales"
    )
    
    # Fecha y hora de creación del registro
    creado = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    # Fecha y hora de la última actualización
    actualizado = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )
    
    class Meta:
        """
        Configuración de metadatos para el modelo Taller.
        """
        verbose_name = "Taller"
        verbose_name_plural = "Talleres"
        ordering = ['-fecha_inicio', 'nombre']  # Ordenar por fecha de inicio descendente y luego por nombre
    
    def __str__(self):
        """
        Representación de texto del taller.
        
        Returns:
            str: Nombre del taller con fechas
        """
        return f"{self.nombre} ({self.fecha_inicio.strftime('%d/%m/%Y')} - {self.fecha_fin.strftime('%d/%m/%Y')})"
    
    def inscritos_count(self):
        """
        Calcula el número de participantes inscritos en el taller.
        
        Returns:
            int: Número de participantes inscritos
        """
        return self.participante_set.count()
    
    def disponibilidad(self):
        """
        Calcula el número de plazas disponibles en el taller.
        
        Returns:
            int: Número de plazas disponibles
        """
        return max(0, self.capacidad - self.inscritos_count())
    
    def esta_lleno(self):
        """
        Determina si el taller está lleno (alcanzó su capacidad máxima).
        
        Returns:
            bool: True si está lleno, False en caso contrario
        """
        return self.inscritos_count() >= self.capacidad
    
    def porcentaje_ocupacion(self):
        """
        Calcula el porcentaje de ocupación del taller.
        
        Returns:
            float: Porcentaje de ocupación (0-100)
        """
        if self.capacidad <= 0:
            return 0
        return (self.inscritos_count() / self.capacidad) * 100


class Participante(models.Model):
    """
    Modelo que representa a un participante inscrito en un taller.
    
    Puede ser una beneficiaria ya registrada en el sistema o una persona externa.
    Permite hacer seguimiento de la asistencia y progreso de cada participante.
    """
    
    # Relación con el taller al que está inscrito
    taller = models.ForeignKey(
        Taller,
        on_delete=models.CASCADE,
        verbose_name="Taller",
        help_text="Taller en el que está inscrito el participante"
    )
    
    # Relación opcional con una beneficiaria existente
    beneficiaria = models.ForeignKey(
        Beneficiaria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Beneficiaria",
        help_text="Seleccione si el participante es una beneficiaria ya registrada"
    )
    
    # Datos personales (requeridos si no es una beneficiaria existente)
    nombres = models.CharField(
        max_length=100,
        verbose_name="Nombres",
        help_text="Nombres del participante",
        blank=True,
        null=True
    )
    
    apellidos = models.CharField(
        max_length=100,
        verbose_name="Apellidos",
        help_text="Apellidos del participante",
        blank=True,
        null=True
    )
    
    dni = models.CharField(
        max_length=8,
        verbose_name="DNI",
        help_text="Número de DNI",
        blank=True,
        null=True
    )
    
    # Fecha de nacimiento (opcional)
    fecha_nacimiento = models.DateField(
        verbose_name="Fecha de nacimiento",
        help_text="Fecha de nacimiento del participante",
        blank=True,
        null=True
    )
    
    telefono = models.CharField(
        max_length=15,
        verbose_name="Teléfono",
        help_text="Número de contacto",
        blank=True,
        null=True
    )
    
    email = models.EmailField(
        verbose_name="Correo electrónico",
        help_text="Dirección de correo electrónico",
        blank=True,
        null=True
    )
    
    # Fecha de inscripción
    fecha_inscripcion = models.DateField(
        verbose_name="Fecha de inscripción",
        auto_now_add=True,
        help_text="Fecha en que se registró la inscripción"
    )
    
    # Estado de la inscripción
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de confirmación'),
        ('CONFIRMADO', 'Confirmado'),
        ('CANCELADO', 'Cancelado'),
        ('FINALIZADO', 'Finalizado'),
    ]
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='CONFIRMADO',
        verbose_name="Estado de la inscripción"
    )
    
    # Notas adicionales sobre el participante
    notas = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas",
        help_text="Observaciones o información adicional sobre el participante"
    )
    
    class Meta:
        """
        Configuración de metadatos para el modelo Participante.
        """
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"
        ordering = ['taller', 'apellidos', 'nombres']
        # Un participante sólo puede inscribirse una vez en cada taller
        unique_together = [['taller', 'beneficiaria'], ['taller', 'dni']]
    
    def __str__(self):
        """
        Representación de texto del participante.
        
        Returns:
            str: Nombre completo del participante
        """
        if self.beneficiaria:
            return f"{self.beneficiaria.nombres} {self.beneficiaria.apellidos}"
        else:
            return f"{self.nombres} {self.apellidos}"
    
    def nombre_completo(self):
        """
        Obtiene el nombre completo del participante.
        
        Returns:
            str: Nombre completo del participante
        """
        if self.beneficiaria:
            return f"{self.beneficiaria.nombres} {self.beneficiaria.apellidos}"
        else:
            return f"{self.nombres} {self.apellidos}"
    
    def clean(self):
        """
        Validaciones personalizadas para el modelo.
        
        Ensures:
            - Si no hay beneficiaria, se requieren los campos nombres, apellidos y DNI
            - Si hay beneficiaria, los campos de identificación personal son opcionales
        
        Raises:
            ValidationError: Si no se cumplen las validaciones
        """
        from django.core.exceptions import ValidationError
        
        # Si no se selecciona una beneficiaria, los campos personales son obligatorios
        if not self.beneficiaria:
            if not self.nombres:
                raise ValidationError({'nombres': 'Este campo es obligatorio si no se selecciona una beneficiaria'})
            if not self.apellidos:
                raise ValidationError({'apellidos': 'Este campo es obligatorio si no se selecciona una beneficiaria'})
            if not self.dni:
                raise ValidationError({'dni': 'Este campo es obligatorio si no se selecciona una beneficiaria'})


class Asistencia(models.Model):
    """
    Modelo que registra la asistencia de los participantes a cada sesión del taller.
    
    Permite llevar un control de asistencia por fecha y por participante.
    """
    
    # Relación con el participante
    participante = models.ForeignKey(
        Participante,
        on_delete=models.CASCADE,
        verbose_name="Participante",
        help_text="Participante cuya asistencia se registra"
    )
    
    # Fecha de la sesión
    fecha = models.DateField(
        verbose_name="Fecha de la sesión",
        help_text="Fecha de la sesión del taller"
    )
    
    # Estado de asistencia
    ASISTENCIA_CHOICES = [
        ('PRESENTE', 'Presente'),
        ('TARDANZA', 'Tardanza'),
        ('AUSENTE', 'Ausente'),
        ('JUSTIFICADO', 'Ausencia justificada'),
    ]
    estado = models.CharField(
        max_length=20,
        choices=ASISTENCIA_CHOICES,
        default='PRESENTE',
        verbose_name="Estado de asistencia"
    )
    
    # Observaciones sobre la asistencia
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones",
        help_text="Notas sobre la asistencia o comportamiento"
    )
    
    # Registro de quién tomó la asistencia
    registrado_por = models.CharField(
        max_length=100,
        verbose_name="Registrado por",
        help_text="Persona que registró la asistencia"
    )
    
    # Fecha y hora del registro
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )
    
    class Meta:
        """
        Configuración de metadatos para el modelo Asistencia.
        """
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        ordering = ['-fecha', 'participante']
        # Un participante solo puede tener un registro de asistencia por fecha y taller
        unique_together = ['participante', 'fecha']
    
    def __str__(self):
        """
        Representación de texto de la asistencia.
        
        Returns:
            str: Información básica del registro de asistencia
        """
        return f"{self.participante} - {self.fecha.strftime('%d/%m/%Y')} - {self.get_estado_display()}"


class Certificado(models.Model):
    """
    Modelo para registrar los certificados emitidos a los participantes.
    
    Almacena información sobre el certificado, como fecha de emisión,
    código único, y estado (emitido, revocado, etc.).
    """
    
    # Relación con el participante
    participante = models.ForeignKey(
        Participante,
        on_delete=models.CASCADE,
        verbose_name="Participante",
        help_text="Participante al que se emite el certificado"
    )
    
    # Código único del certificado
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código del certificado",
        help_text="Código único que identifica al certificado",
        default=generar_codigo_certificado
    )
    
    # Fecha de emisión
    fecha_emision = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de emisión",
        help_text="Fecha y hora en que se emitió el certificado"
    )
    
    # Estado del certificado
    ESTADO_CHOICES = [
        ('EMITIDO', 'Emitido'),
        ('REVOCADO', 'Revocado'),
    ]
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='EMITIDO',
        verbose_name="Estado del certificado"
    )
    
    # Observaciones
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones",
        help_text="Observaciones o notas adicionales sobre el certificado"
    )
    
    class Meta:
        """
        Configuración de metadatos para el modelo Certificado.
        """
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"
        ordering = ['-fecha_emision']
    
    def __str__(self):
        """
        Representación de texto del certificado.
        
        Returns:
            str: Información básica del certificado
        """
        return f"Certificado {self.codigo} - {self.participante.nombre_completo()}"


class Evaluacion(models.Model):
    """
    Modelo para registrar evaluaciones o logros de los participantes en los talleres.
    
    Permite hacer seguimiento del progreso y aprendizaje de cada participante.
    """
    
    # Relación con el participante
    participante = models.ForeignKey(
        Participante,
        on_delete=models.CASCADE,
        verbose_name="Participante",
        help_text="Participante que está siendo evaluado"
    )
    
    # Fecha de evaluación
    fecha = models.DateField(
        verbose_name="Fecha de evaluación",
        help_text="Fecha en que se realiza la evaluación"
    )
    
    # Título de la evaluación
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Título o nombre de la evaluación"
    )
    
    # Descripción de la evaluación
    descripcion = models.TextField(
        verbose_name="Descripción",
        help_text="Descripción detallada de la evaluación o criterios evaluados"
    )
    
    # Calificación (opcional, según el tipo de evaluación)
    calificacion = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Calificación",
        help_text="Calificación numérica (si aplica)",
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    
    # Nivel de logro
    LOGRO_CHOICES = [
        ('EXCELENTE', 'Excelente'),
        ('BUENO', 'Bueno'),
        ('REGULAR', 'Regular'),
        ('NECESITA_MEJORAR', 'Necesita mejorar'),
        ('NO_EVALUADO', 'No evaluado'),
    ]
    nivel_logro = models.CharField(
        max_length=20,
        choices=LOGRO_CHOICES,
        default='NO_EVALUADO',
        verbose_name="Nivel de logro"
    )
    
    # Comentarios sobre la evaluación
    comentarios = models.TextField(
        blank=True,
        null=True,
        verbose_name="Comentarios",
        help_text="Comentarios adicionales sobre el desempeño o logros"
    )
    
    # Registrado por
    evaluador = models.CharField(
        max_length=100,
        verbose_name="Evaluador",
        help_text="Persona que realizó la evaluación"
    )
    
    # Fecha y hora del registro
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )
    
    class Meta:
        """
        Configuración de metadatos para el modelo Evaluacion.
        """
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"
        ordering = ['-fecha', 'participante']
    
    def __str__(self):
        """
        Representación de texto de la evaluación.
        
        Returns:
            str: Información básica de la evaluación
        """
        return f"{self.titulo} - {self.participante} - {self.fecha.strftime('%d/%m/%Y')}"


class Material(models.Model):
    """
    Modelo para registrar los materiales asociados a un taller.
    
    Permite hacer seguimiento de documentos, presentaciones, videos y otros
    recursos utilizados en los talleres.
    """
    
    # Relación con el taller
    taller = models.ForeignKey(
        Taller,
        on_delete=models.CASCADE,
        verbose_name="Taller",
        help_text="Taller al que pertenece el material"
    )
    
    # Título del material
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Título o nombre del material"
    )
    
    # Descripción del material
    descripcion = models.TextField(
        verbose_name="Descripción",
        help_text="Descripción breve del contenido del material"
    )
    
    # Tipo de material
    TIPO_CHOICES = [
        ('DOCUMENTO', 'Documento'),
        ('PRESENTACION', 'Presentación'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('IMAGEN', 'Imagen'),
        ('ENLACE', 'Enlace'),
        ('OTRO', 'Otro'),
    ]
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='DOCUMENTO',
        verbose_name="Tipo de material"
    )
    
    # Archivo adjunto (opcional)
    archivo = models.FileField(
        upload_to='talleres/materiales/',
        blank=True,
        null=True,
        verbose_name="Archivo",
        help_text="Archivo del material (si aplica)"
    )
    
    # URL externa (opcional)
    url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL",
        help_text="Enlace externo al material (si aplica)"
    )
    
    # Fecha de creación
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    # Fecha de actualización
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )
    
    # Autor o creador del material
    autor = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Autor",
        help_text="Autor o creador del material"
    )
    
    class Meta:
        """
        Configuración de metadatos para el modelo Material.
        """
        verbose_name = "Material"
        verbose_name_plural = "Materiales"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        """
        Representación de texto del material.
        
        Returns:
            str: Título del material y tipo
        """
        return f"{self.titulo} ({self.get_tipo_display()})"
    
    def tiene_archivo(self):
        """
        Verifica si el material tiene un archivo adjunto.
        
        Returns:
            bool: True si tiene archivo, False en caso contrario
        """
        return bool(self.archivo)
    
    def tiene_url(self):
        """
        Verifica si el material tiene una URL asociada.
        
        Returns:
            bool: True si tiene URL, False en caso contrario
        """
        return bool(self.url)
