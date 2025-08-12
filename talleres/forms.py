from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms.widgets import DateInput
from django.utils import timezone

# Validadores personalizados
telefono_validator = RegexValidator(
    regex=r'^\d{9}$',
    message="El teléfono debe contener exactamente 9 dígitos numéricos."
)

dni_validator = RegexValidator(
    regex=r'^\d{8}$',
    message="El DNI debe contener exactamente 8 dígitos numéricos."
)

from .models import Taller, Participante, Asistencia, Evaluacion, Material
from beneficiarias.models import Beneficiaria


class TallerForm(forms.ModelForm):
    """
    Formulario para crear y editar talleres.
    
    Incluye validaciones para asegurar que las fechas sean válidas y que
    la capacidad sea un número positivo.
    """
    # Campos de observaciones opcionales
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=False,  # Descripción opcional
    )
    
    notas = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Notas opcionales
    )
    
    class Meta:
        model = Taller
        fields = [
            'nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 
            'horario', 'lugar', 'capacidad', 'facilitador', 
            'estado', 'notas'
        ]
        widgets = {
            # Usar widgets de tipo date para los campos de fecha
            'fecha_inicio': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'horario': forms.TextInput(attrs={'class': 'form-control'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'facilitador': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        """
        Validación personalizada para el formulario completo.
        
        Verifica que la fecha de fin sea posterior a la fecha de inicio
        y que la capacidad sea un número positivo.
        
        Raises:
            ValidationError: Si hay errores en la validación
        """
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        capacidad = cleaned_data.get('capacidad')
        
        # Verificar que la fecha de fin sea posterior a la de inicio
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            self.add_error(
                'fecha_fin', 
                ValidationError('La fecha de finalización debe ser posterior a la fecha de inicio.')
            )
        
        # Verificar que la capacidad sea un número positivo
        if capacidad and capacidad <= 0:
            self.add_error(
                'capacidad',
                ValidationError('La capacidad debe ser un número positivo.')
            )
        
        return cleaned_data


class ParticipanteForm(forms.ModelForm):
    """
    Formulario para crear y editar participantes.
    
    Incluye lógica para manejar participantes que son beneficiarias existentes
    y participantes externos.
    """
    
    # Campo oculto para mantener compatibilidad
    buscar_beneficiaria = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    # Campo para fecha de nacimiento (opcional)
    fecha_nacimiento = forms.DateField(
        required=False,
        label="Fecha de Nacimiento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Opcional: Fecha de nacimiento del participante"
    )
    
    # Redefinimos los campos que necesitan validación especial
    telefono = forms.CharField(
        max_length=9, 
        validators=[telefono_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123456789'}),
        help_text="Ingrese un número de 9 dígitos",
        required=True
    )
    
    dni = forms.CharField(
        max_length=8,
        validators=[dni_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678'}),
        help_text="Ingrese un DNI de 8 dígitos",
        required=False  # Se validará en clean()
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=False,  # Email opcional
    )
    
    # Campos de observaciones opcionales
    notas = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Notas opcionales
    )
    
    class Meta:
        model = Participante
        fields = [
            'taller', 'beneficiaria', 'nombres', 'apellidos', 
            'dni', 'telefono', 'email', 'estado', 'notas'
        ]
        widgets = {
            # Campo oculto para el taller (se establecerá desde la vista)
            'taller': forms.HiddenInput(),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario y personaliza los campos según sea necesario.
        
        Si se proporciona un taller_id en kwargs, se filtra el campo de taller
        para mostrar solo ese taller.
        """
        taller_id = kwargs.pop('taller_id', None)
        super().__init__(*args, **kwargs)
        
        # Si se proporciona un taller_id, filtrar el campo de taller
        if taller_id:
            self.fields['taller'].queryset = Taller.objects.filter(id=taller_id)
            self.fields['taller'].initial = taller_id
        
        # Hacer que el campo beneficiaria sea oculto
        self.fields['beneficiaria'].widget = forms.HiddenInput()
        
        # Hacer que los campos personales sean inicialmente opcionales
        # (su obligatoriedad se validará en clean() según si hay beneficiaria o no)
        self.fields['nombres'].required = False
        self.fields['apellidos'].required = False
        self.fields['dni'].required = False
    
    def clean(self):
        """
        Validación personalizada del formulario.
        
        Verifica que se proporcionen los datos personales necesarios.
        
        Raises:
            ValidationError: Si hay errores en la validación
        """
        cleaned_data = super().clean()
        nombres = cleaned_data.get('nombres')
        apellidos = cleaned_data.get('apellidos')
        dni = cleaned_data.get('dni')
        
        # Los campos personales son siempre obligatorios
        if not nombres:
            self.add_error('nombres', ValidationError('Este campo es obligatorio.'))
        
        if not apellidos:
            self.add_error('apellidos', ValidationError('Este campo es obligatorio.'))
        
        if not dni:
            self.add_error('dni', ValidationError('Este campo es obligatorio.'))
        
        return cleaned_data


class AsistenciaForm(forms.ModelForm):
    """
    Formulario para registrar la asistencia de participantes.
    
    Permite registrar la asistencia de un participante en una fecha específica.
    """
    # Campos de observaciones opcionales
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        required=False,  # Observaciones opcionales
    )
    
    class Meta:
        model = Asistencia
        fields = ['participante', 'fecha', 'estado', 'observaciones', 'registrado_por']
        widgets = {
            'fecha': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'participante': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'registrado_por': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario con opciones personalizadas.
        
        Si se proporciona un taller_id en kwargs, se filtran los participantes
        para mostrar solo los de ese taller.
        """
        taller_id = kwargs.pop('taller_id', None)
        super().__init__(*args, **kwargs)
        
        # Establecer la fecha actual como valor predeterminado
        self.fields['fecha'].initial = timezone.now().date()
        
        # Si se proporciona un taller_id, filtrar los participantes
        if taller_id:
            self.fields['participante'].queryset = Participante.objects.filter(
                taller_id=taller_id,
                estado='CONFIRMADO'  # Solo participantes confirmados
            )
    
    def clean(self):
        """
        Validación personalizada del formulario.
        
        Verifica que la fecha de asistencia esté dentro del período del taller.
        
        Raises:
            ValidationError: Si hay errores en la validación
        """
        cleaned_data = super().clean()
        participante = cleaned_data.get('participante')
        fecha = cleaned_data.get('fecha')
        
        if participante and fecha:
            taller = participante.taller
            
            # Verificar que la fecha esté dentro del período del taller
            if fecha < taller.fecha_inicio or fecha > taller.fecha_fin:
                self.add_error(
                    'fecha',
                    ValidationError('La fecha de asistencia debe estar dentro del período del taller.')
                )
        
        return cleaned_data


class AsistenciaMasivaForm(forms.Form):
    """
    Formulario para registrar asistencia masiva de varios participantes a la vez.
    
    Permite seleccionar una fecha y registrar la asistencia de múltiples
    participantes en una sola operación.
    """
    
    fecha = forms.DateField(
        label="Fecha de la sesión",
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date()
    )
    
    registrado_por = forms.CharField(
        label="Registrado por",
        max_length=100,
        help_text="Persona que registra la asistencia",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario con opciones personalizadas.
        
        Recibe una lista de participantes para generar campos dinámicos
        para cada uno de ellos.
        
        Args:
            participantes: Lista de objetos Participante
        """
        self.participantes = kwargs.pop('participantes', [])
        super().__init__(*args, **kwargs)
        
        # Crear campos dinámicos para cada participante
        for participante in self.participantes:
            field_name = f"estado_{participante.id}"
            self.fields[field_name] = forms.ChoiceField(
                label=participante.nombre_completo(),
                choices=Asistencia.ASISTENCIA_CHOICES,
                initial='PRESENTE',
                widget=forms.Select(attrs={'class': 'form-select'})
            )
            
            # Campo de observaciones opcional
            obs_field_name = f"observaciones_{participante.id}"
            self.fields[obs_field_name] = forms.CharField(
                label="Observaciones",
                required=False,
                widget=forms.Textarea(attrs={'rows': 1, 'class': 'form-control'})
            )


class EvaluacionForm(forms.ModelForm):
    """
    Formulario para crear y editar evaluaciones de participantes.
    
    Permite registrar las evaluaciones o logros de los participantes en los talleres.
    """
    # Campos de observaciones opcionales
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Descripción opcional
    )
    
    comentarios = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Comentarios opcionales
    )
    
    class Meta:
        model = Evaluacion
        fields = [
            'participante', 'fecha', 'titulo', 'descripcion', 
            'calificacion', 'nivel_logro', 'comentarios', 'evaluador'
        ]
        widgets = {
            'fecha': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'participante': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'calificacion': forms.NumberInput(attrs={'class': 'form-control'}),
            'nivel_logro': forms.Select(attrs={'class': 'form-select'}),
            'evaluador': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario con opciones personalizadas.
        
        Si se proporciona un taller_id en kwargs, se filtran los participantes
        para mostrar solo los de ese taller.
        """
        taller_id = kwargs.pop('taller_id', None)
        super().__init__(*args, **kwargs)
        
        # Establecer la fecha actual como valor predeterminado
        self.fields['fecha'].initial = timezone.now().date()
        
        # Si se proporciona un taller_id, filtrar los participantes
        if taller_id:
            self.fields['participante'].queryset = Participante.objects.filter(
                taller_id=taller_id,
                estado='CONFIRMADO'  # Solo participantes confirmados
            )


class MaterialForm(forms.ModelForm):
    """
    Formulario para crear y editar materiales de taller.
    
    Permite añadir materiales como documentos, enlaces, etc., a un taller.
    """
    # Campos de observaciones opcionales
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Descripción opcional
    )
    
    class Meta:
        model = Material
        fields = [
            'taller', 'titulo', 'descripcion', 'tipo',
            'archivo', 'url', 'autor'
        ]
        widgets = {
            # Campo oculto para el taller (se establecerá desde la vista)
            'taller': forms.HiddenInput(),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario con opciones personalizadas.
        
        Si se proporciona un taller_id en kwargs, se filtra el campo de taller
        para mostrar solo ese taller.
        """
        taller_id = kwargs.pop('taller_id', None)
        super().__init__(*args, **kwargs)
        
        # Si se proporciona un taller_id, filtrar el campo de taller
        if taller_id:
            self.fields['taller'].queryset = Taller.objects.filter(id=taller_id)
            self.fields['taller'].initial = taller_id
    
    def clean(self):
        """
        Validación personalizada del formulario.
        
        Verifica que se proporcione al menos un archivo o una URL.
        
        Raises:
            ValidationError: Si hay errores en la validación
        """
        cleaned_data = super().clean()
        archivo = cleaned_data.get('archivo')
        url = cleaned_data.get('url')
        
        # Verificar que se proporcione al menos un archivo o una URL
        if not archivo and not url:
            self.add_error(
                None,
                ValidationError('Debe proporcionar un archivo o una URL para el material.')
            )
        
        return cleaned_data
