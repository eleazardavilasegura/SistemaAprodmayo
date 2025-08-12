from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import models
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Importaciones de modelos de otras aplicaciones
from beneficiarias.models import Beneficiaria
from talleres.models import Taller
from finanzas.models import Ingreso, Egreso, Socio

from .models import Usuario
from .forms import RegistroUsuarioForm, PerfilUsuarioForm, CambioPasswordForm, LoginForm
from .decorators import AdminRequiredMixin, permiso_beneficiarias_required, permiso_finanzas_required, permiso_talleres_required, permiso_reportes_required

# Funciones de comprobación de roles
def is_admin(user):
    """
    Verifica si el usuario tiene rol de administrador.
    """
    return user.is_authenticated and user.is_admin()

@method_decorator(csrf_exempt, name='dispatch')  # Solo para desarrollo, no recomendado para producción
class CustomLoginView(LoginView):
    """
    Vista personalizada para el inicio de sesión.
    """
    form_class = LoginForm
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        """
        Actualiza la fecha del último acceso al iniciar sesión exitosamente.
        """
        response = super().form_valid(form)
        self.request.user.fecha_ultimo_acceso = timezone.now()
        self.request.user.save()
        return response

@login_required
def perfil(request):
    """
    Vista para mostrar y editar el perfil del usuario actual.
    """
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
            return redirect('perfil')
    else:
        form = PerfilUsuarioForm(instance=request.user)
    
    return render(request, 'usuarios/perfil.html', {
        'form': form,
    })

@login_required
def cambiar_password(request):
    """
    Vista para cambiar la contraseña del usuario actual.
    """
    if request.method == 'POST':
        form = CambioPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '¡Tu contraseña ha sido actualizada exitosamente!')
            return redirect('perfil')
    else:
        form = CambioPasswordForm(request.user)
    
    return render(request, 'usuarios/cambiar_password.html', {
        'form': form,
    })

class UsuarioListView(AdminRequiredMixin, ListView):
    """
    Vista para listar todos los usuarios (solo para administradores).
    """
    model = Usuario
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(email__icontains=search)
            )
        
        # Filtrar por rol
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filtrar por estado
        status = self.request.GET.get('status')
        if status:
            is_active = status == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        return queryset

class UsuarioCreateView(AdminRequiredMixin, CreateView):
    """
    Vista para crear nuevos usuarios (solo para administradores).
    """
    model = Usuario
    form_class = RegistroUsuarioForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario_list')
    
    def form_valid(self, form):
        """
        Procesa el formulario si es válido.
        Si el rol es administrador, se asignan todos los permisos.
        """
        usuario = form.save(commit=False)
        
        # Si el rol es administrador, asignar todos los permisos
        if usuario.role == Usuario.ADMINISTRADOR:
            usuario.permiso_beneficiarias = True
            usuario.permiso_finanzas = True
            usuario.permiso_talleres = True
            usuario.permiso_reportes = True
        
        usuario.save()
        messages.success(self.request, f'¡Usuario {usuario.username} creado exitosamente!')
        return super().form_valid(form)

class UsuarioUpdateView(AdminRequiredMixin, UpdateView):
    """
    Vista para actualizar usuarios existentes (solo para administradores).
    """
    model = Usuario
    form_class = RegistroUsuarioForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario_list')
    
    def get_form(self, form_class=None):
        """
        Excluir los campos de contraseña al editar.
        """
        form = super().get_form(form_class)
        if form_class is None and self.object:
            # Si estamos editando, excluimos los campos de contraseña
            form.fields.pop('password1', None)
            form.fields.pop('password2', None)
        return form
    
    def form_valid(self, form):
        """
        Procesa el formulario si es válido.
        Si el rol es administrador, se asignan todos los permisos.
        """
        usuario = form.save(commit=False)
        
        # Si el rol es administrador, asignar todos los permisos
        if usuario.role == Usuario.ADMINISTRADOR:
            usuario.permiso_beneficiarias = True
            usuario.permiso_finanzas = True
            usuario.permiso_talleres = True
            usuario.permiso_reportes = True
        
        usuario.save()
        messages.success(self.request, f'¡Usuario {usuario.username} actualizado exitosamente!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Para mostrar permisos correctamente en el formulario
        if self.object.role == Usuario.ADMINISTRADOR:
            context['form'].initial.update({
                'permiso_beneficiarias': True,
                'permiso_finanzas': True,
                'permiso_talleres': True,
                'permiso_reportes': True
            })
        return context

class UsuarioDeleteView(AdminRequiredMixin, DeleteView):
    """
    Vista para eliminar usuarios (solo para administradores).
    """
    model = Usuario
    template_name = 'usuarios/usuario_confirm_delete.html'
    success_url = reverse_lazy('usuario_list')
    
    def get_queryset(self):
        """
        Evitar que se eliminen usuarios administradores
        """
        queryset = super().get_queryset()
        return queryset.exclude(role=Usuario.ADMINISTRADOR)
    
    def delete(self, request, *args, **kwargs):
        """
        Elimina el usuario y muestra un mensaje de éxito.
        """
        usuario = self.get_object()
        messages.success(request, f'¡El usuario {usuario.username} ha sido eliminado exitosamente!')
        return super().delete(request, *args, **kwargs)

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Vista del Dashboard principal del sistema.
    Muestra estadísticas generales y accesos rápidos a los diferentes módulos.
    """
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener estadísticas para el dashboard
        context['beneficiarias_count'] = Beneficiaria.objects.count()
        context['talleres_activos'] = Taller.objects.filter(fecha_fin__gte=timezone.now().date()).count()
        context['socios_count'] = Socio.objects.filter(estado='ACTIVO').count()
        
        # Calcular balance financiero
        total_ingresos = Ingreso.objects.aggregate(total=models.Sum('monto'))['total'] or 0
        total_egresos = Egreso.objects.aggregate(total=models.Sum('monto'))['total'] or 0
        context['balance_total'] = total_ingresos - total_egresos
        
        # Fecha actual para el dashboard
        context['now'] = timezone.now()
        
        return context
