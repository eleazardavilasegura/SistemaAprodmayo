"""
Modelos para el módulo de finanzas.

Este módulo contiene los modelos para gestionar:
- Categorías de ingresos y egresos
- Socios y sus cuotas
- Registros de ingresos
- Registros de egresos
- Informes financieros
"""

from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.core.validators import MinValueValidator


class Categoria(models.Model):
    """
    Modelo para categorías de ingresos y egresos.
    Permite clasificar las transacciones financieras.
    """
    TIPO_CHOICES = (
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso'),
    )
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['tipo', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class Socio(models.Model):
    """
    Modelo para los socios de APRODMAYO.
    Registra información básica y de contacto de los socios.
    """
    ESTADO_CHOICES = (
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
    )
    
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    documento_identidad = models.CharField(max_length=20, blank=True)
    fecha_registro = models.DateField(default=timezone.now)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='ACTIVO')
    cuota_mensual = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Socio"
        verbose_name_plural = "Socios"
        ordering = ['apellidos', 'nombres']
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    def get_cuotas_pagadas(self):
        """Retorna el total de cuotas pagadas por el socio"""
        return self.pagos.aggregate(total=Sum('monto'))['total'] or 0
    
    def get_ultima_cuota(self):
        """Retorna la fecha de la última cuota pagada"""
        ultimo_pago = self.pagos.order_by('-fecha').first()
        return ultimo_pago.fecha if ultimo_pago else None
    
    def esta_al_dia(self):
        """
        Verifica si el socio está al día con sus cuotas.
        
        Un socio está al día si:
        1. Ha realizado un pago en los últimos 40 días, o
        2. Se registró hace menos de 40 días y aún no ha realizado pagos.
        """
        ultimo_pago = self.get_ultima_cuota()
        hoy = timezone.now().date()
        
        # Si existe un pago, verificamos que no tenga más de 40 días
        if ultimo_pago:
            dias_desde_ultimo_pago = (hoy - ultimo_pago).days
            return dias_desde_ultimo_pago <= 40
        
        # Si no hay pagos, verificamos si el socio se registró recientemente
        # (se da un plazo de 40 días desde el registro para realizar el primer pago)
        dias_desde_registro = (hoy - self.fecha_registro).days
        return dias_desde_registro <= 40


class PagoSocio(models.Model):
    """
    Modelo para registrar los pagos de cuotas de los socios.
    """
    socio = models.ForeignKey(
        Socio, 
        on_delete=models.CASCADE,
        related_name='pagos'
    )
    fecha = models.DateField(default=timezone.now)
    monto = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    periodo_correspondiente = models.CharField(max_length=20, blank=True, help_text="Ej: Enero 2025")
    metodo_pago = models.CharField(max_length=50, blank=True)
    comprobante = models.CharField(max_length=50, blank=True)
    observaciones = models.TextField(blank=True)
    registrado_por = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Pago de Socio"
        verbose_name_plural = "Pagos de Socios"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Pago de {self.socio} - {self.fecha} - {self.monto}"
    
    @classmethod
    def get_next_comprobante(cls):
        """
        Genera el siguiente número de comprobante de forma secuencial.
        El formato es un número secuencial (1, 2, 3, etc.)
        
        Returns:
            String: El siguiente número de comprobante
        """
        # Buscar el último comprobante
        ultimo_pago = cls.objects.order_by('-id').first()
        
        # Si no hay pagos anteriores, empezar desde 1
        if not ultimo_pago or not ultimo_pago.comprobante:
            return "1"
        
        # Intentar extraer el número del último comprobante
        try:
            ultimo_numero = int(ultimo_pago.comprobante)
            return str(ultimo_numero + 1)
        except (ValueError, TypeError):
            # Si el comprobante anterior no es un número, comenzar desde 1
            return "1"


class Ingreso(models.Model):
    """
    Modelo para registrar ingresos financieros que no son cuotas de socios.
    """
    fecha = models.DateField(default=timezone.now)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        limit_choices_to={'tipo': 'INGRESO'}
    )
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    comprobante = models.CharField(max_length=50, blank=True)
    metodo_ingreso = models.CharField(max_length=50, blank=True)
    observaciones = models.TextField(blank=True)
    registrado_por = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.fecha} - {self.descripcion} - {self.monto}"


class Egreso(models.Model):
    """
    Modelo para registrar los gastos o egresos financieros.
    """
    fecha = models.DateField(default=timezone.now)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        limit_choices_to={'tipo': 'EGRESO'}
    )
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    comprobante = models.CharField(max_length=50, blank=True)
    metodo_pago = models.CharField(max_length=50, blank=True)
    proveedor = models.CharField(max_length=100, blank=True)
    observaciones = models.TextField(blank=True)
    registrado_por = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Egreso"
        verbose_name_plural = "Egresos"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.fecha} - {self.descripcion} - {self.monto}"


class InformeFinanciero(models.Model):
    """
    Modelo para almacenar informes financieros periódicos.
    """
    PERIODO_CHOICES = (
        ('MENSUAL', 'Mensual'),
        ('TRIMESTRAL', 'Trimestral'),
        ('ANUAL', 'Anual'),
        ('PERSONALIZADO', 'Personalizado'),
    )
    
    titulo = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo_periodo = models.CharField(max_length=20, choices=PERIODO_CHOICES)
    total_ingresos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_egresos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)
    creado_por = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Informe Financiero"
        verbose_name_plural = "Informes Financieros"
        ordering = ['-fecha_fin']
    
    def __str__(self):
        return f"{self.titulo} ({self.fecha_inicio} - {self.fecha_fin})"
    
    def generar_informe(self):
        """
        Calcula los totales de ingresos y egresos para el período especificado
        """
        # Calcular ingresos (cuotas + otros ingresos)
        cuotas = PagoSocio.objects.filter(
            fecha__gte=self.fecha_inicio,
            fecha__lte=self.fecha_fin
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        otros_ingresos = Ingreso.objects.filter(
            fecha__gte=self.fecha_inicio,
            fecha__lte=self.fecha_fin
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        self.total_ingresos = cuotas + otros_ingresos
        
        # Calcular egresos
        self.total_egresos = Egreso.objects.filter(
            fecha__gte=self.fecha_inicio,
            fecha__lte=self.fecha_fin
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        # Calcular saldo
        self.saldo = self.total_ingresos - self.total_egresos
        self.save()
