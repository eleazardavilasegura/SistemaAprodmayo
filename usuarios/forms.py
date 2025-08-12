from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.validators import RegexValidator
from .models import Usuario

# Validadores personalizados
telefono_validator = RegexValidator(
    regex=r'^\d{9}$',
    message="El teléfono debe contener exactamente 9 dígitos numéricos."
)

dni_validator = RegexValidator(
    regex=r'^\d{8}$',
    message="El DNI debe contener exactamente 8 dígitos numéricos."
)

class LoginForm(AuthenticationForm):
    """
    Formulario personalizado para inicio de sesión.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )


class RegistroUsuarioForm(UserCreationForm):
    """
    Formulario para registrar nuevos usuarios.
    """
    # Redefinimos los campos que necesitan validación especial
    telefono = forms.CharField(
        max_length=9, 
        validators=[telefono_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '123456789'
        }),
        help_text="Ingrese un número de 9 dígitos",
        required=True
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'correo@ejemplo.com'
        }),
        required=True  # El email es requerido para usuarios del sistema
    )
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email', 'telefono', 
            'role', 'password1', 'password2', 'imagen_perfil', 'is_active',
            'permiso_beneficiarias', 'permiso_finanzas', 'permiso_talleres', 'permiso_reportes'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre de usuario'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Apellido'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
            'imagen_perfil': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'permiso_beneficiarias': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'permiso_finanzas': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'permiso_talleres': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'permiso_reportes': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
        
        # Por defecto, activar la cuenta
        self.fields['is_active'].initial = True
        
        # Si el rol es administrador, habilitar todos los permisos por defecto
        if kwargs.get('instance') and kwargs['instance'].role == Usuario.ADMINISTRADOR:
            self.fields['permiso_beneficiarias'].initial = True
            self.fields['permiso_finanzas'].initial = True
            self.fields['permiso_talleres'].initial = True
            self.fields['permiso_reportes'].initial = True
            
    def clean(self):
        """
        Validación adicional para asegurar que los administradores tengan todos los permisos.
        """
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        # Si el usuario es administrador, se asignan todos los permisos
        if role == Usuario.ADMINISTRADOR:
            cleaned_data['permiso_beneficiarias'] = True
            cleaned_data['permiso_finanzas'] = True
            cleaned_data['permiso_talleres'] = True
            cleaned_data['permiso_reportes'] = True
            
        return cleaned_data


class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulario para actualizar el perfil de usuario.
    """
    # Redefinimos los campos que necesitan validación especial
    telefono = forms.CharField(
        max_length=9, 
        validators=[telefono_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123456789'}),
        help_text="Ingrese un número de 9 dígitos",
        required=True
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True  # El email es requerido para usuarios del sistema
    )
    
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'imagen_perfil']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen_perfil': forms.FileInput(attrs={'class': 'form-control'})
        }


class CambioPasswordForm(PasswordChangeForm):
    """
    Formulario personalizado para cambio de contraseña.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
