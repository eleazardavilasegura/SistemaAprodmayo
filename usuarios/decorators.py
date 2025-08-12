from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from functools import wraps
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles):
    """
    Decorador para restringir el acceso a vistas basadas en funciones según el rol del usuario.
    
    Args:
        allowed_roles: Lista de roles permitidos
        
    Returns:
        La vista si el usuario tiene el rol adecuado, de lo contrario un error 403
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return wrapper
    return decorator

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin para restringir el acceso a vistas basadas en clases solo para administradores.
    """
    login_url = reverse_lazy('login')
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'administrador'


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin para restringir el acceso a vistas basadas en clases según los roles de usuario.
    """
    login_url = reverse_lazy('login')
    allowed_roles = []
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in self.allowed_roles

# Nuevos decoradores y mixins para permisos específicos
def permiso_beneficiarias_required(function):
    """
    Decorador que verifica si el usuario tiene permiso para acceder al módulo de beneficiarias.
    """
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.can_access_beneficiarias():
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "No tienes permiso para acceder al módulo de beneficiarias.")
            if request.user.is_authenticated:
                return redirect('dashboard')
            return redirect('login')
    return wrapper

def permiso_finanzas_required(function):
    """
    Decorador que verifica si el usuario tiene permiso para acceder al módulo de finanzas.
    """
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.can_access_finanzas():
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "No tienes permiso para acceder al módulo de finanzas.")
            if request.user.is_authenticated:
                return redirect('dashboard')
            return redirect('login')
    return wrapper

def permiso_talleres_required(function):
    """
    Decorador que verifica si el usuario tiene permiso para acceder al módulo de talleres.
    """
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.can_access_talleres():
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "No tienes permiso para acceder al módulo de talleres.")
            if request.user.is_authenticated:
                return redirect('dashboard')
            return redirect('login')
    return wrapper

def permiso_reportes_required(function):
    """
    Decorador que verifica si el usuario tiene permiso para acceder a los reportes.
    """
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.can_access_reportes():
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "No tienes permiso para acceder a los reportes.")
            if request.user.is_authenticated:
                return redirect('dashboard')
            return redirect('login')
    return wrapper

# Mixins para vistas basadas en clases
class BeneficiariasRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin para restringir el acceso a vistas relacionadas con beneficiarias.
    """
    login_url = reverse_lazy('login')
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.can_access_beneficiarias()
    
    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para acceder al módulo de beneficiarias.")
        return redirect('dashboard')

class FinanzasRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin para restringir el acceso a vistas relacionadas con finanzas.
    """
    login_url = reverse_lazy('login')
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.can_access_finanzas()
    
    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para acceder al módulo de finanzas.")
        return redirect('dashboard')

class TalleresRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin para restringir el acceso a vistas relacionadas con talleres.
    """
    login_url = reverse_lazy('login')
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.can_access_talleres()
    
    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para acceder al módulo de talleres.")
        return redirect('dashboard')

class ReportesRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin para restringir el acceso a vistas relacionadas con reportes.
    """
    login_url = reverse_lazy('login')
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.can_access_reportes()
    
    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para acceder a los reportes.")
        return redirect('dashboard')
