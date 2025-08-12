from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

class Usuario(AbstractUser):
    """
    Modelo personalizado de usuario que extiende el modelo de usuario base de Django.
    
    Incluye campos adicionales para los roles y permisos específicos de APRODMAYO.
    """
    # Definición de roles disponibles
    ADMINISTRADOR = 'administrador'
    EMPLEADO = 'empleado'
    
    ROLE_CHOICES = [
        (ADMINISTRADOR, 'Administrador'),
        (EMPLEADO, 'Empleado'),
    ]
    
    # Campos adicionales
    role = models.CharField(_('Rol'), max_length=15, choices=ROLE_CHOICES, default=EMPLEADO)
    telefono = models.CharField(_('Teléfono'), max_length=15, blank=True, null=True)
    imagen_perfil = models.ImageField(_('Imagen de perfil'), upload_to='perfiles/', blank=True, null=True)
    fecha_ultimo_acceso = models.DateTimeField(_('Último acceso'), blank=True, null=True)
    
    # Permisos de módulos específicos
    permiso_beneficiarias = models.BooleanField(_('Acceso a Beneficiarias'), default=True)
    permiso_finanzas = models.BooleanField(_('Acceso a Finanzas'), default=False)
    permiso_talleres = models.BooleanField(_('Acceso a Talleres'), default=False)
    permiso_reportes = models.BooleanField(_('Acceso a Reportes'), default=False)
    
    # Relación ManyToMany personalizada
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='usuarios',
        related_query_name='usuario',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='usuarios',
        related_query_name='usuario',
    )
    
    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
    
    def is_admin(self):
        """
        Determina si el usuario tiene el rol de administrador.
        
        Returns:
            bool: True si el usuario es administrador, False en caso contrario
        """
        return self.role == self.ADMINISTRADOR
    
    def is_empleado(self):
        """
        Determina si el usuario tiene el rol de empleado.
        
        Returns:
            bool: True si el usuario es empleado, False en caso contrario
        """
        return self.role == self.EMPLEADO
        
    def can_access_beneficiarias(self):
        """
        Determina si el usuario tiene acceso al módulo de beneficiarias.
        
        Returns:
            bool: True si tiene permiso o es administrador, False en caso contrario
        """
        return self.is_admin() or self.permiso_beneficiarias
        
    def can_access_finanzas(self):
        """
        Determina si el usuario tiene acceso al módulo de finanzas.
        
        Returns:
            bool: True si tiene permiso o es administrador, False en caso contrario
        """
        return self.is_admin() or self.permiso_finanzas
        
    def can_access_talleres(self):
        """
        Determina si el usuario tiene acceso al módulo de talleres.
        
        Returns:
            bool: True si tiene permiso o es administrador, False en caso contrario
        """
        return self.is_admin() or self.permiso_talleres
        
    def can_access_reportes(self):
        """
        Determina si el usuario tiene acceso a los reportes del sistema.
        
        Returns:
            bool: True si tiene permiso o es administrador, False en caso contrario
        """
        return self.is_admin() or self.permiso_reportes
