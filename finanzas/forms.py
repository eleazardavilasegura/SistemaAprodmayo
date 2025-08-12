"""
Formularios para el módulo de finanzas.
"""

from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import Categoria, Socio, PagoSocio, Ingreso, Egreso, InformeFinanciero
from django.utils import timezone
import datetime

# Validadores personalizados
telefono_validator = RegexValidator(
    regex=r'^\d{9}$',
    message="El teléfono debe contener exactamente 9 dígitos numéricos."
)

dni_validator = RegexValidator(
    regex=r'^\d{8}$',
    message="El DNI debe contener exactamente 8 dígitos numéricos."
)

class CategoriaForm(forms.ModelForm):
    """Formulario para crear y editar categorías financieras"""
    # Campos de observaciones opcionales
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Descripción opcional
    )
    
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'tipo', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SocioForm(forms.ModelForm):
    """Formulario para crear y editar socios"""
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
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Observaciones opcionales
    )
    
    class Meta:
        model = Socio
        fields = [
            'nombres', 'apellidos', 'documento_identidad', 'fecha_registro',
            'telefono', 'correo', 'direccion', 'estado',
            'cuota_mensual', 'observaciones'
        ]
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_registro': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'cuota_mensual': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }


class PagoSocioForm(forms.ModelForm):
    """Formulario para registrar pagos de socios"""
    # Opciones para los meses
    OPCIONES_MESES = [
        ('1', 'Enero'),
        ('2', 'Febrero'),
        ('3', 'Marzo'),
        ('4', 'Abril'),
        ('5', 'Mayo'),
        ('6', 'Junio'),
        ('7', 'Julio'),
        ('8', 'Agosto'),
        ('9', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),
    ]
    
    # Creamos campos separados para mes y año
    periodo_mes = forms.ChoiceField(
        choices=OPCIONES_MESES,
        label="Mes correspondiente",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    # Opciones para los años (año actual y los próximos)
    def get_anios_opciones():
        anio_actual = timezone.now().year
        return [(str(anio_actual + i), str(anio_actual + i)) for i in range(-1, 3)]
    
    OPCIONES_ANIOS = get_anios_opciones()
    
    periodo_anio = forms.ChoiceField(
        choices=OPCIONES_ANIOS,
        label="Año correspondiente",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    # Opción para registrar también como ingreso
    registrar_ingreso = forms.BooleanField(
        label="Registrar también como ingreso",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = PagoSocio
        fields = [
            'socio', 'fecha', 'monto', 'periodo_mes', 'periodo_anio',
            'metodo_pago', 'comprobante', 'observaciones', 'registrado_por'
        ]
        widgets = {
            'socio': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
            'comprobante': forms.TextInput(attrs={'class': 'form-control'}),
            'registrado_por': forms.Select(attrs={'class': 'form-select'}),
        }
        
    # Campos de observaciones opcionales
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Observaciones opcionales
    )
    
    def __init__(self, *args, **kwargs):
        socio_id = kwargs.pop('socio_id', None)
        super().__init__(*args, **kwargs)
        
        # Fecha actual para predeterminar los valores
        fecha_actual = timezone.now().date()
        mes_actual = fecha_actual.month
        anio_actual = fecha_actual.year
        
        # Predeterminar el mes y año actuales
        self.fields['periodo_mes'].initial = str(mes_actual)
        self.fields['periodo_anio'].initial = str(anio_actual)
        
        # Predeterminar la fecha de hoy para el pago
        self.fields['fecha'].initial = fecha_actual
        
        # Generar número de comprobante automático si es un nuevo registro
        if not self.instance.pk:
            self.fields['comprobante'].initial = PagoSocio.get_next_comprobante()
            # Hacer el campo comprobante de solo lectura para nuevos registros
            self.fields['comprobante'].widget.attrs['readonly'] = True
        
        if socio_id:
            # Si se proporciona un ID de socio, pre-seleccionamos ese socio
            self.fields['socio'].initial = socio_id
            self.fields['socio'].widget.attrs['readonly'] = True
            
            # Pre-completar el monto con la cuota mensual del socio
            try:
                socio = Socio.objects.get(id=socio_id)
                self.fields['monto'].initial = socio.cuota_mensual
                
                # Verificar si es un socio nuevo
                dias_desde_registro = (fecha_actual - socio.fecha_registro).days
                if dias_desde_registro <= 7:
                    # Si es un socio nuevo, agregamos una nota
                    self.fields['observaciones'].initial = (
                        "Primer pago del socio registrado el " + 
                        socio.fecha_registro.strftime("%d/%m/%Y") +
                        ". Este pago corresponde al mes de registro (mes actual)."
                    )
            except Socio.DoesNotExist:
                pass
                
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Construir el periodo correspondiente a partir de los campos mes y año
        mes_nombre = dict(self.OPCIONES_MESES).get(self.cleaned_data['periodo_mes'])
        instance.periodo_correspondiente = f"{mes_nombre} {self.cleaned_data['periodo_anio']}"
        
        if commit:
            instance.save()
            
            # Si se seleccionó registrar como ingreso, creamos el registro correspondiente
            if self.cleaned_data.get('registrar_ingreso'):
                from .models import Ingreso, Categoria
                try:
                    categoria = Categoria.objects.get(nombre='Cuota de Socio', tipo='INGRESO')
                except Categoria.DoesNotExist:
                    # Si no existe la categoría, la creamos
                    categoria = Categoria.objects.create(
                        nombre='Cuota de Socio',
                        descripcion='Pagos de cuotas mensuales de socios',
                        tipo='INGRESO',
                        activo=True
                    )
                
                # Crear el registro de ingreso
                Ingreso.objects.create(
                    fecha=instance.fecha,
                    categoria=categoria,
                    descripcion=f"Cuota de socio: {instance.socio.nombres} {instance.socio.apellidos} - {instance.periodo_correspondiente}",
                    monto=instance.monto,
                    comprobante=instance.comprobante,
                    metodo_ingreso=instance.metodo_pago,
                    observaciones=instance.observaciones,
                    registrado_por=instance.registrado_por
                )
        
        return instance


class IngresoForm(forms.ModelForm):
    """Formulario para registrar ingresos"""
    # Campos de observaciones opcionales
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Observaciones opcionales
    )
    
    class Meta:
        model = Ingreso
        fields = [
            'fecha', 'categoria', 'descripcion', 'monto',
            'comprobante', 'metodo_ingreso', 'observaciones', 'registrado_por'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'comprobante': forms.TextInput(attrs={'class': 'form-control'}),
            'metodo_ingreso': forms.Select(attrs={'class': 'form-select'}),
            'registrado_por': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtramos las categorías para mostrar solo las de tipo INGRESO
        self.fields['categoria'].queryset = Categoria.objects.filter(tipo='INGRESO', activo=True)


class EgresoForm(forms.ModelForm):
    """Formulario para registrar egresos"""
    # Campos de observaciones opcionales
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Observaciones opcionales
    )
    
    class Meta:
        model = Egreso
        fields = [
            'fecha', 'categoria', 'descripcion', 'monto',
            'comprobante', 'metodo_pago', 'proveedor', 'observaciones', 'registrado_por'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'comprobante': forms.TextInput(attrs={'class': 'form-control'}),
            'metodo_pago': forms.TextInput(attrs={'class': 'form-control'}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'registrado_por': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtramos las categorías para mostrar solo las de tipo EGRESO
        self.fields['categoria'].queryset = Categoria.objects.filter(tipo='EGRESO', activo=True)


class InformeFinancieroForm(forms.ModelForm):
    """Formulario para crear informes financieros"""
    # Campos de observaciones opcionales
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,  # Observaciones opcionales
    )
    
    class Meta:
        model = InformeFinanciero
        fields = [
            'titulo', 'fecha_inicio', 'fecha_fin', 
            'tipo_periodo', 'observaciones', 'creado_por'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo_periodo': forms.Select(attrs={'class': 'form-select'}),
            'creado_por': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        """Validación personalizada para las fechas del informe"""
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                self.add_error('fecha_inicio', 'La fecha de inicio no puede ser posterior a la fecha de fin')
            
            # Verificar que el período no sea demasiado largo (máximo 1 año)
            if (fecha_fin - fecha_inicio).days > 366:
                self.add_error('fecha_fin', 'El período del informe no puede ser mayor a un año')
        
        return cleaned_data


class FiltroTransaccionesForm(forms.Form):
    """
    Formulario para filtrar transacciones por fecha, categoría, etc.
    Se utiliza para filtrar la vista de ingresos y egresos.
    """
    fecha_inicio = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Desde"
    )
    fecha_fin = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Hasta"
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Categoría"
    )
    min_monto = forms.DecimalField(
        required=False, 
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Monto mínimo"
    )
    max_monto = forms.DecimalField(
        required=False, 
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Monto máximo"
    )
    
    def __init__(self, *args, tipo=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tipo:
            # Filtramos las categorías según el tipo (INGRESO o EGRESO)
            self.fields['categoria'].queryset = Categoria.objects.filter(tipo=tipo)
    
    def clean(self):
        """Validación personalizada para las fechas y montos"""
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        min_monto = cleaned_data.get('min_monto')
        max_monto = cleaned_data.get('max_monto')
        
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            self.add_error('fecha_inicio', 'La fecha de inicio no puede ser posterior a la fecha de fin')
        
        if min_monto and max_monto and min_monto > max_monto:
            self.add_error('min_monto', 'El monto mínimo no puede ser mayor que el monto máximo')
        
        return cleaned_data
