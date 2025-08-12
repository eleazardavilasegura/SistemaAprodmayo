from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import Beneficiaria, Acompanante, Hijo, SeguimientoCaso

# Validadores personalizados
telefono_validator = RegexValidator(
    regex=r'^\d{9}$',
    message="El teléfono debe contener exactamente 9 dígitos numéricos."
)

dni_validator = RegexValidator(
    regex=r'^\d{8}$',
    message="El DNI debe contener exactamente 8 dígitos numéricos."
)


class BeneficiariaForm(forms.ModelForm):
    # Redefinimos los campos que necesitan validación especial
    telefono = forms.CharField(
        max_length=9, 
        validators=[telefono_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123456789'}),
        help_text="Ingrese un número de 9 dígitos",
        required=True
    )
    
    documento_identidad = forms.CharField(
        max_length=8,
        validators=[dni_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678'}),
        help_text="Ingrese un DNI de 8 dígitos",
        required=True
    )
    
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=False,  # Email opcional
    )
    
    # Campos de observaciones opcionales
    notas_seguimiento = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Notas opcionales
    )
    
    # Campo de fecha_nacimiento opcional
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,  # Fecha de nacimiento opcional
    )
    
    class Meta:
        model = Beneficiaria
        fields = [
            'nombres', 'apellidos', 'edad', 'fecha_nacimiento',
            'documento_identidad', 'tipo_documento', 'direccion',
            'telefono', 'correo', 'estado_civil', 'nivel_educativo',
            'ocupacion', 'situacion_laboral', 'motivo_consulta',
            'tipo_violencia', 'descripcion_situacion', 'problemas_salud',
            'medicacion', 'tiene_hijos', 'numero_hijos',
            'situacion_vivienda', 'seguimiento_requerido',
            'notas_seguimiento', 'recibido_por', 'fecha_ingreso', 'hora_ingreso'
        ]
        widgets = {
            # Inputs de texto
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'ocupacion': forms.TextInput(attrs={'class': 'form-control'}),
            'recibido_por': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_hijos': forms.NumberInput(attrs={'class': 'form-control'}),
            
            # Selectores
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'nivel_educativo': forms.Select(attrs={'class': 'form-select'}),
            'situacion_laboral': forms.Select(attrs={'class': 'form-select'}),
            'tipo_violencia': forms.Select(attrs={'class': 'form-select'}),
            'situacion_vivienda': forms.Select(attrs={'class': 'form-select'}),
            
            # Campos de fecha y hora
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_ingreso': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            
            # Áreas de texto
            'descripcion_situacion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'motivo_consulta': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'problemas_salud': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'medicacion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notas_seguimiento': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            
            # Checkboxes
            'tiene_hijos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'seguimiento_requerido': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        tiene_hijos = cleaned_data.get('tiene_hijos')
        numero_hijos = cleaned_data.get('numero_hijos')
        
        if tiene_hijos and (numero_hijos is None or numero_hijos == 0):
            self.add_error('numero_hijos', 'Si tiene hijos, debe indicar cuántos')
        
        return cleaned_data


class AcompananteForm(forms.ModelForm):
    # Redefinimos los campos que necesitan validación especial
    telefono = forms.CharField(
        max_length=9, 
        validators=[telefono_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123456789'}),
        help_text="Ingrese un número de 9 dígitos",
        required=True
    )
    
    documento_identidad = forms.CharField(
        max_length=8,
        validators=[dni_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678'}),
        help_text="Ingrese un DNI de 8 dígitos",
        required=True
    )
    
    # Campos de observaciones opcionales
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Observaciones opcionales
    )
    
    class Meta:
        model = Acompanante
        fields = [
            'nombres', 'apellidos', 'parentesco', 'edad',
            'documento_identidad', 'telefono', 'direccion',
            'observaciones'
        ]
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'parentesco': forms.Select(attrs={'class': 'form-select'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }


class HijoForm(forms.ModelForm):
    # Campos de fecha de nacimiento opcionales
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,  # Fecha de nacimiento opcional
    )
    
    # Campos de observaciones opcionales
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Observaciones opcionales
    )
    
    class Meta:
        model = Hijo
        fields = [
            'nombres', 'apellidos', 'edad', 'fecha_nacimiento',
            'genero', 'escolaridad', 'vive_con_beneficiaria', 
            'observaciones'
        ]
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'escolaridad': forms.TextInput(attrs={'class': 'form-control'}),
            'vive_con_beneficiaria': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SeguimientoCasoForm(forms.ModelForm):
    # Campos de observaciones opcionales
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=False,  # Descripción opcional
    )
    
    acuerdos = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Acuerdos opcionales
    )
    
    class Meta:
        model = SeguimientoCaso
        fields = [
            'fecha', 'tipo_atencion', 'profesional',
            'descripcion', 'acuerdos', 'proxima_cita'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo_atencion': forms.Select(attrs={'class': 'form-select'}),
            'profesional': forms.TextInput(attrs={'class': 'form-control'}),
            'proxima_cita': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
