from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q
from .models import Beneficiaria, Acompanante, Hijo, SeguimientoCaso
from .forms import BeneficiariaForm, AcompananteForm, HijoForm, SeguimientoCasoForm

# Vistas para Beneficiarias
class BeneficiariaListView(LoginRequiredMixin, ListView):
    model = Beneficiaria
    template_name = 'beneficiarias/beneficiaria_list.html'
    context_object_name = 'beneficiarias'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Beneficiaria.objects.filter(
                nombres__icontains=query
            ) | Beneficiaria.objects.filter(
                apellidos__icontains=query
            ) | Beneficiaria.objects.filter(
                documento_identidad__icontains=query
            )
        return Beneficiaria.objects.all().order_by('-fecha_ingreso')

class BeneficiariaDetailView(LoginRequiredMixin, DetailView):
    model = Beneficiaria
    template_name = 'beneficiarias/beneficiaria_detail.html'
    context_object_name = 'beneficiaria'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acompanantes'] = self.object.acompanantes.all()
        context['hijos'] = self.object.hijos.all()
        context['seguimientos'] = self.object.seguimientos.all().order_by('-fecha')
        return context

class BeneficiariaCreateView(LoginRequiredMixin, CreateView):
    model = Beneficiaria
    form_class = BeneficiariaForm
    template_name = 'beneficiarias/beneficiaria_form.html'
    success_url = reverse_lazy('beneficiaria_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Beneficiaria registrada exitosamente")
        return super().form_valid(form)

class BeneficiariaUpdateView(LoginRequiredMixin, UpdateView):
    model = Beneficiaria
    form_class = BeneficiariaForm
    template_name = 'beneficiarias/beneficiaria_form.html'
    
    def get_success_url(self):
        return reverse_lazy('beneficiaria_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, "Información actualizada exitosamente")
        return super().form_valid(form)

class BeneficiariaDeleteView(LoginRequiredMixin, DeleteView):
    model = Beneficiaria
    template_name = 'beneficiarias/beneficiaria_confirm_delete.html'
    success_url = reverse_lazy('beneficiaria_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Registro eliminado exitosamente")
        return super().delete(request, *args, **kwargs)

# Vistas para Acompañantes
class AcompananteCreateView(LoginRequiredMixin, CreateView):
    model = Acompanante
    form_class = AcompananteForm
    template_name = 'beneficiarias/acompanante_form.html'
    
    def form_valid(self, form):
        form.instance.beneficiaria_id = self.kwargs['pk']
        messages.success(self.request, "Acompañante registrado exitosamente")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('beneficiaria_detail', kwargs={'pk': self.kwargs['pk']})

class AcompananteUpdateView(LoginRequiredMixin, UpdateView):
    model = Acompanante
    form_class = AcompananteForm
    template_name = 'beneficiarias/acompanante_form.html'
    
    def get_success_url(self):
        return reverse_lazy('beneficiaria_detail', kwargs={'pk': self.object.beneficiaria.pk})

class AcompananteDeleteView(LoginRequiredMixin, DeleteView):
    model = Acompanante
    template_name = 'beneficiarias/acompanante_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('beneficiaria_detail', kwargs={'pk': self.object.beneficiaria.pk})

# Vistas para Hijos
class HijoCreateView(LoginRequiredMixin, CreateView):
    model = Hijo
    form_class = HijoForm
    template_name = 'beneficiarias/hijo_form.html'
    
    def form_valid(self, form):
        form.instance.beneficiaria_id = self.kwargs['pk']
        messages.success(self.request, "Hijo registrado exitosamente")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('beneficiaria_detail', kwargs={'pk': self.kwargs['pk']})

class HijoUpdateView(LoginRequiredMixin, UpdateView):
    model = Hijo
    form_class = HijoForm
    template_name = 'beneficiarias/hijo_form.html'
    
    def get_success_url(self):
        return reverse_lazy('beneficiaria_detail', kwargs={'pk': self.object.beneficiaria.pk})

class HijoDeleteView(LoginRequiredMixin, DeleteView):
    model = Hijo
    template_name = 'beneficiarias/hijo_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('beneficiaria_detail', kwargs={'pk': self.object.beneficiaria.pk})

# Vistas para Seguimiento de Casos
class SeguimientoCreateView(LoginRequiredMixin, CreateView):
    model = SeguimientoCaso
    form_class = SeguimientoCasoForm
    template_name = 'beneficiarias/seguimiento_form.html'
    
    def form_valid(self, form):
        form.instance.beneficiaria_id = self.kwargs['pk']
        messages.success(self.request, "Seguimiento registrado exitosamente")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('beneficiaria_detail', kwargs={'pk': self.kwargs['pk']})

class SeguimientoUpdateView(LoginRequiredMixin, UpdateView):
    model = SeguimientoCaso
    form_class = SeguimientoCasoForm
    template_name = 'beneficiarias/seguimiento_form.html'
    
    def get_success_url(self):
        return reverse_lazy('beneficiaria_detail', kwargs={'pk': self.object.beneficiaria.pk})

class SeguimientoDeleteView(LoginRequiredMixin, DeleteView):
    model = SeguimientoCaso
    template_name = 'beneficiarias/seguimiento_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('beneficiaria_detail', kwargs={'pk': self.object.beneficiaria.pk})

# API para beneficiarias
def buscar_beneficiarias_api(request):
    """
    API para buscar beneficiarias por nombre, apellido o DNI.
    Devuelve un JSON con las beneficiarias que coinciden con el término de búsqueda.
    """
    term = request.GET.get('term', '')
    if len(term) < 3:
        return JsonResponse([], safe=False)
    
    beneficiarias = Beneficiaria.objects.filter(
        Q(nombres__icontains=term) | 
        Q(apellidos__icontains=term) | 
        Q(documento_identidad__icontains=term)
    )[:10]  # Limitamos a 10 resultados
    
    data = []
    for b in beneficiarias:
        data.append({
            'id': b.id,
            'nombres': b.nombres,
            'apellidos': b.apellidos,
            'dni': b.documento_identidad,
            'telefono': b.telefono,
            'correo': b.correo if hasattr(b, 'correo') else None
        })
    
    return JsonResponse(data, safe=False)

def detalle_beneficiaria_api(request, pk):
    """
    API para obtener los detalles de una beneficiaria específica.
    Devuelve un JSON con la información de la beneficiaria.
    """
    try:
        beneficiaria = Beneficiaria.objects.get(pk=pk)
        data = {
            'id': beneficiaria.id,
            'nombres': beneficiaria.nombres,
            'apellidos': beneficiaria.apellidos,
            'dni': beneficiaria.documento_identidad,
            'telefono': beneficiaria.telefono,
            'correo': beneficiaria.correo if hasattr(beneficiaria, 'correo') else None
        }
        return JsonResponse(data)
    except Beneficiaria.DoesNotExist:
        return JsonResponse({'error': 'Beneficiaria no encontrada'}, status=404)
