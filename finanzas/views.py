"""
Vistas para el módulo de finanzas.

Este módulo contiene vistas para:
- Gestión de categorías financieras
- Gestión de socios y sus pagos
- Registro de ingresos y egresos
- Generación de informes financieros
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from usuarios.decorators import FinanzasRequiredMixin, permiso_finanzas_required
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import TruncMonth, TruncYear
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import csv

from .models import (
    Categoria, Socio, PagoSocio, 
    Ingreso, Egreso, InformeFinanciero
)
from .forms import (
    CategoriaForm, SocioForm, PagoSocioForm, 
    IngresoForm, EgresoForm, InformeFinancieroForm,
    FiltroTransaccionesForm
)


# Vistas para Categorías
class CategoriaListView(FinanzasRequiredMixin, ListView):
    """Lista todas las categorías financieras.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Categoria
    template_name = 'finanzas/categoria_list.html'
    context_object_name = 'categorias'
    
    def get_queryset(self):
        return Categoria.objects.all().order_by('tipo', 'nombre')


class CategoriaCreateView(FinanzasRequiredMixin, CreateView):
    """Crea una nueva categoría financiera.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Categoria
    form_class = CategoriaForm
    template_name = 'finanzas/categoria_form.html'
    success_url = reverse_lazy('categoria_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Categoría creada exitosamente")
        return super().form_valid(form)


class CategoriaUpdateView(FinanzasRequiredMixin, UpdateView):
    """Actualiza una categoría existente.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Categoria
    form_class = CategoriaForm
    template_name = 'finanzas/categoria_form.html'
    success_url = reverse_lazy('categoria_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Categoría actualizada exitosamente")
        return super().form_valid(form)


class CategoriaDeleteView(FinanzasRequiredMixin, DeleteView):
    """Elimina una categoría.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Categoria
    template_name = 'finanzas/categoria_confirm_delete.html'
    success_url = reverse_lazy('categoria_list')
    
    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, "Categoría eliminada exitosamente")
            return response
        except Exception as e:
            messages.error(request, f"No se puede eliminar la categoría porque está siendo utilizada: {str(e)}")
            return redirect('categoria_list')


# Vistas para Socios
class SocioListView(FinanzasRequiredMixin, ListView):
    """Lista todos los socios.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Socio
    template_name = 'finanzas/socio_list.html'
    context_object_name = 'socios'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        estado = self.request.GET.get('estado')
        situacion = self.request.GET.get('situacion')
        
        socios = Socio.objects.all()
        
        if query:
            socios = socios.filter(
                nombres__icontains=query
            ) | socios.filter(
                apellidos__icontains=query
            ) | socios.filter(
                documento_identidad__icontains=query
            )
        
        if estado:
            socios = socios.filter(estado=estado)
        
        # Filtrar manualmente por situación de pagos
        if situacion:
            # Obtenemos primero todos los IDs que cumplen la condición
            filtrados_ids = []
            for socio in socios:
                esta_al_dia = socio.esta_al_dia()
                if (situacion == 'AL_DIA' and esta_al_dia) or (situacion == 'ATRASADO' and not esta_al_dia):
                    filtrados_ids.append(socio.id)
            
            # Filtramos la consulta por los IDs obtenidos
            socios = socios.filter(id__in=filtrados_ids)
            
        return socios.order_by('apellidos', 'nombres')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Añadimos situación de pagos a cada socio para mostrar en la plantilla
        for socio in context['object_list']:
            socio.situacion_pagos = 'AL_DIA' if socio.esta_al_dia() else 'ATRASADO'
        
        # Contamos socios activos y con atrasos
        socios_activos = Socio.objects.filter(estado='ACTIVO').count()
        
        # Contamos socios con atrasos
        socios_con_atrasos = 0
        for socio in Socio.objects.filter(estado='ACTIVO'):
            if not socio.esta_al_dia():
                socios_con_atrasos += 1
        
        context['socios_activos'] = socios_activos
        context['socios_con_atrasos'] = socios_con_atrasos
        
        return context


class SocioDetailView(FinanzasRequiredMixin, DetailView):
    """Muestra el detalle de un socio y su historial de pagos.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Socio
    template_name = 'finanzas/socio_detail.html'
    context_object_name = 'socio'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagos'] = self.object.pagos.all().order_by('-fecha')
        
        # Calcular totales de pagos
        total_pagado = self.object.pagos.aggregate(total=Sum('monto'))['total'] or 0
        context['total_pagado'] = total_pagado
        
        # Determinar estado de pagos (al día o atrasado)
        ultimo_pago = self.object.pagos.order_by('-fecha').first()
        if ultimo_pago:
            context['ultimo_pago'] = ultimo_pago
            dias_desde_ultimo_pago = (timezone.now().date() - ultimo_pago.fecha).days
            context['dias_desde_ultimo_pago'] = dias_desde_ultimo_pago
        
        # Usar el método mejorado para determinar si está al día
        context['esta_al_dia'] = self.object.esta_al_dia()
        
        # Calcular días desde el registro si no hay pagos
        dias_desde_registro = (timezone.now().date() - self.object.fecha_registro).days
        context['dias_desde_registro'] = dias_desde_registro
        
        return context


class SocioCreateView(FinanzasRequiredMixin, CreateView):
    """Crea un nuevo socio.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Socio
    form_class = SocioForm
    template_name = 'finanzas/socio_form.html'
    success_url = reverse_lazy('socio_list')
    
    def get_initial(self):
        """Inicializa la fecha de registro con la fecha actual"""
        initial = super().get_initial()
        initial['fecha_registro'] = timezone.now().date()
        return initial
    
    def form_valid(self, form):
        """Guarda el socio y muestra un mensaje de éxito"""
        messages.success(self.request, "Socio registrado exitosamente")
        
        # Guardamos el socio primero para poder registrar el pago
        self.object = form.save()
        
        # Obtener el mes y año actual
        fecha_actual = timezone.now().date()
        mes_actual = fecha_actual.strftime("%B")
        anio_actual = fecha_actual.year
        
        # Añadimos un mensaje específico sobre el pago de la cuota del mes actual
        messages.info(
            self.request,
            f"El socio debe pagar la cuota correspondiente al mes de {mes_actual} {anio_actual} aunque se haya "
            f"registrado en los últimos días del mes. Por favor, registre el pago inmediatamente."
        )
        
        # Redireccionar al formulario de pago inmediatamente después del registro
        self.success_url = reverse_lazy('pago_socio_create', kwargs={'socio_id': self.object.pk})
        
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirecciona al formulario de registro de pago después de crear un socio"""
        # Redirigimos directamente al formulario de pago para el socio recién creado
        return reverse_lazy('pago_socio_create', kwargs={'socio_id': self.object.pk})


class SocioUpdateView(FinanzasRequiredMixin, UpdateView):
    """Actualiza datos de un socio.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Socio
    form_class = SocioForm
    template_name = 'finanzas/socio_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, "Datos del socio actualizados exitosamente")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('socio_detail', kwargs={'pk': self.object.pk})


class SocioDeleteView(FinanzasRequiredMixin, DeleteView):
    """Elimina un socio.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Socio
    template_name = 'finanzas/socio_confirm_delete.html'
    success_url = reverse_lazy('socio_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Socio eliminado exitosamente")
        return super().delete(request, *args, **kwargs)


# Vistas para Pagos de Socios
class PagoSocioCreateView(FinanzasRequiredMixin, CreateView):
    """Registra un nuevo pago de un socio.
    Requiere permiso para acceder al módulo de finanzas."""
    model = PagoSocio
    form_class = PagoSocioForm
    template_name = 'finanzas/pago_socio_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'socio_id' in self.kwargs:
            kwargs['socio_id'] = self.kwargs['socio_id']
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir la fecha actual al contexto
        context['now'] = timezone.now()
        
        # Si hay un socio_id en los parámetros, obtenemos el objeto socio
        if 'socio_id' in self.kwargs:
            try:
                socio = Socio.objects.get(id=self.kwargs['socio_id'])
                context['socio'] = socio
                
                # Si el socio es recién registrado y es el primer pago
                dias_desde_registro = (timezone.now().date() - socio.fecha_registro).days
                if dias_desde_registro <= 7 and not socio.pagos.exists():
                    messages.info(
                        self.request, 
                        f"Este socio se registró hace {dias_desde_registro} días. "
                        f"Debe pagar la cuota correspondiente al mes actual ({timezone.now().strftime('%B %Y')}), "
                        f"aunque se haya registrado en los últimos días del mes."
                    )
            except Socio.DoesNotExist:
                pass
            
        # Añadir el siguiente número de comprobante al contexto
        context['siguiente_comprobante'] = PagoSocio.get_next_comprobante()
        
        return context
    
    def form_valid(self, form):
        # Asegurarnos de que el comprobante sea el correcto (secuencial)
        pago = form.save(commit=False)
        if not pago.comprobante:
            pago.comprobante = PagoSocio.get_next_comprobante()
        
        # Construir un mensaje más específico
        mes_nombre = dict(form.OPCIONES_MESES).get(form.cleaned_data['periodo_mes'])
        anio = form.cleaned_data['periodo_anio']
        messages.success(
            self.request, 
            f"Pago por el mes de {mes_nombre} {anio} registrado exitosamente con comprobante N° {pago.comprobante}"
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('socio_detail', kwargs={'pk': self.object.socio.pk})


class PagoSocioUpdateView(FinanzasRequiredMixin, UpdateView):
    """Actualiza un pago existente.
    Requiere permiso para acceder al módulo de finanzas."""
    model = PagoSocio
    form_class = PagoSocioForm
    template_name = 'finanzas/pago_socio_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # El número de comprobante no debería cambiar al editar
        form.fields['comprobante'].widget.attrs['readonly'] = True
        return form
    
    def form_valid(self, form):
        # Asegurar que no se cambie el número de comprobante
        if self.object.comprobante:
            form.instance.comprobante = self.object.comprobante
        
        # Construir un mensaje más específico
        mes_nombre = dict(form.OPCIONES_MESES).get(form.cleaned_data['periodo_mes'])
        anio = form.cleaned_data['periodo_anio']
        messages.success(
            self.request, 
            f"Pago por el mes de {mes_nombre} {anio} actualizado exitosamente"
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('socio_detail', kwargs={'pk': self.object.socio.pk})


class PagoSocioDeleteView(FinanzasRequiredMixin, DeleteView):
    """Elimina un pago.
    Requiere permiso para acceder al módulo de finanzas."""
    model = PagoSocio
    template_name = 'finanzas/pago_socio_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('socio_detail', kwargs={'pk': self.object.socio.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Pago eliminado exitosamente")
        return super().delete(request, *args, **kwargs)


# Vistas para Ingresos
class IngresoListView(FinanzasRequiredMixin, ListView):
    """Lista todos los ingresos (no incluye cuotas de socios).
    Requiere permiso para acceder al módulo de finanzas."""
    model = Ingreso
    template_name = 'finanzas/ingreso_list.html'
    context_object_name = 'ingresos'
    paginate_by = 15
    
    def get_queryset(self):
        form = FiltroTransaccionesForm(self.request.GET, tipo='INGRESO')
        queryset = Ingreso.objects.all()
        
        if form.is_valid():
            # Aplicar filtros si se proporcionan
            if form.cleaned_data['fecha_inicio']:
                queryset = queryset.filter(fecha__gte=form.cleaned_data['fecha_inicio'])
            
            if form.cleaned_data['fecha_fin']:
                queryset = queryset.filter(fecha__lte=form.cleaned_data['fecha_fin'])
            
            if form.cleaned_data['categoria']:
                queryset = queryset.filter(categoria=form.cleaned_data['categoria'])
            
            if form.cleaned_data['min_monto']:
                queryset = queryset.filter(monto__gte=form.cleaned_data['min_monto'])
            
            if form.cleaned_data['max_monto']:
                queryset = queryset.filter(monto__lte=form.cleaned_data['max_monto'])
        
        return queryset.order_by('-fecha')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_form'] = FiltroTransaccionesForm(self.request.GET, tipo='INGRESO')
        
        # Calcular total de ingresos filtrados
        queryset = self.get_queryset()
        context['total_ingresos'] = queryset.aggregate(total=Sum('monto'))['total'] or 0
        
        return context


class IngresoCreateView(FinanzasRequiredMixin, CreateView):
    """Registra un nuevo ingreso.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Ingreso
    form_class = IngresoForm
    template_name = 'finanzas/ingreso_form.html'
    success_url = reverse_lazy('ingreso_list')
    
    def get_initial(self):
        initial = super().get_initial()
        initial['fecha'] = timezone.now().date()
        initial['registrado_por'] = self.request.user.get_full_name() if hasattr(self.request.user, 'get_full_name') else self.request.user.username
        return initial
    
    def form_valid(self, form):
        messages.success(self.request, "Ingreso registrado exitosamente")
        return super().form_valid(form)


class IngresoUpdateView(FinanzasRequiredMixin, UpdateView):
    """Actualiza un ingreso existente.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Ingreso
    form_class = IngresoForm
    template_name = 'finanzas/ingreso_form.html'
    success_url = reverse_lazy('ingreso_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Ingreso actualizado exitosamente")
        return super().form_valid(form)


class IngresoDeleteView(FinanzasRequiredMixin, DeleteView):
    """Elimina un ingreso.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Ingreso
    template_name = 'finanzas/ingreso_confirm_delete.html'
    success_url = reverse_lazy('ingreso_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Ingreso eliminado exitosamente")
        return super().delete(request, *args, **kwargs)


# Vistas para Egresos
class EgresoListView(FinanzasRequiredMixin, ListView):
    """Lista todos los egresos.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Egreso
    template_name = 'finanzas/egreso_list.html'
    context_object_name = 'egresos'
    paginate_by = 15
    
    def get_queryset(self):
        form = FiltroTransaccionesForm(self.request.GET, tipo='EGRESO')
        queryset = Egreso.objects.all()
        
        if form.is_valid():
            # Aplicar filtros si se proporcionan
            if form.cleaned_data['fecha_inicio']:
                queryset = queryset.filter(fecha__gte=form.cleaned_data['fecha_inicio'])
            
            if form.cleaned_data['fecha_fin']:
                queryset = queryset.filter(fecha__lte=form.cleaned_data['fecha_fin'])
            
            if form.cleaned_data['categoria']:
                queryset = queryset.filter(categoria=form.cleaned_data['categoria'])
            
            if form.cleaned_data['min_monto']:
                queryset = queryset.filter(monto__gte=form.cleaned_data['min_monto'])
            
            if form.cleaned_data['max_monto']:
                queryset = queryset.filter(monto__lte=form.cleaned_data['max_monto'])
        
        return queryset.order_by('-fecha')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_form'] = FiltroTransaccionesForm(self.request.GET, tipo='EGRESO')
        
        # Calcular total de egresos filtrados
        queryset = self.get_queryset()
        context['total_egresos'] = queryset.aggregate(total=Sum('monto'))['total'] or 0
        
        return context


class EgresoCreateView(FinanzasRequiredMixin, CreateView):
    """Registra un nuevo egreso.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Egreso
    form_class = EgresoForm
    template_name = 'finanzas/egreso_form.html'
    success_url = reverse_lazy('egreso_list')
    
    def get_initial(self):
        initial = super().get_initial()
        initial['fecha'] = timezone.now().date()
        initial['registrado_por'] = self.request.user.get_full_name() if hasattr(self.request.user, 'get_full_name') else self.request.user.username
        return initial
    
    def form_valid(self, form):
        messages.success(self.request, "Egreso registrado exitosamente")
        return super().form_valid(form)


class EgresoUpdateView(FinanzasRequiredMixin, UpdateView):
    """Actualiza un egreso existente.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Egreso
    form_class = EgresoForm
    template_name = 'finanzas/egreso_form.html'
    success_url = reverse_lazy('egreso_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Egreso actualizado exitosamente")
        return super().form_valid(form)


class EgresoDeleteView(FinanzasRequiredMixin, DeleteView):
    """Elimina un egreso.
    Requiere permiso para acceder al módulo de finanzas."""
    model = Egreso
    template_name = 'finanzas/egreso_confirm_delete.html'
    success_url = reverse_lazy('egreso_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Egreso eliminado exitosamente")
        return super().delete(request, *args, **kwargs)


# Vistas para Informes Financieros
class InformeFinancieroListView(FinanzasRequiredMixin, ListView):
    """Lista todos los informes financieros.
    Requiere permiso para acceder al módulo de finanzas."""
    model = InformeFinanciero
    template_name = 'finanzas/informe_list.html'
    context_object_name = 'informes'
    paginate_by = 10


class InformeFinancieroDetailView(FinanzasRequiredMixin, DetailView):
    """Muestra el detalle de un informe financiero.
    Requiere permiso para acceder al módulo de finanzas."""
    model = InformeFinanciero
    template_name = 'finanzas/informe_detail.html'
    context_object_name = 'informe'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener datos detallados para el informe
        informe = self.object
        fecha_inicio = informe.fecha_inicio
        fecha_fin = informe.fecha_fin
        
        # Obtener ingresos detallados
        pagos_socios = PagoSocio.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        ).select_related('socio')
        
        otros_ingresos = Ingreso.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        ).select_related('categoria')
        
        # Obtener egresos detallados
        egresos = Egreso.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        ).select_related('categoria')
        
        # Agrupar por categoría - Formato para los templates
        ingresos_por_categoria_dict = {}
        ingresos_por_categoria = []
        total_pagos_socios = Decimal('0.00')
        
        # Procesar pagos de socios
        for pago in pagos_socios:
            total_pagos_socios += pago.monto
            
        if total_pagos_socios > 0:
            ingresos_por_categoria_dict['Cuotas de Socios'] = total_pagos_socios
            ingresos_por_categoria.append({
                'categoria__nombre': 'Cuotas de Socios',
                'total': float(total_pagos_socios)
            })
        
        # Procesar otros ingresos
        for ingreso in otros_ingresos:
            categoria_nombre = ingreso.categoria.nombre
            if categoria_nombre in ingresos_por_categoria_dict:
                ingresos_por_categoria_dict[categoria_nombre] += ingreso.monto
            else:
                ingresos_por_categoria_dict[categoria_nombre] = ingreso.monto
        
        # Convertir el diccionario a la lista de formato esperado por el template
        for categoria, monto in ingresos_por_categoria_dict.items():
            if categoria != 'Cuotas de Socios':  # Ya lo agregamos antes
                ingresos_por_categoria.append({
                    'categoria__nombre': categoria,
                    'total': float(monto)
                })
        
        # Agrupar egresos por categoría
        egresos_por_categoria_dict = {}
        egresos_por_categoria = []
        for egreso in egresos:
            categoria_nombre = egreso.categoria.nombre
            if categoria_nombre in egresos_por_categoria_dict:
                egresos_por_categoria_dict[categoria_nombre] += egreso.monto
            else:
                egresos_por_categoria_dict[categoria_nombre] = egreso.monto
                
        # Convertir el diccionario a la lista de formato esperado por el template
        for categoria, monto in egresos_por_categoria_dict.items():
            egresos_por_categoria.append({
                'categoria__nombre': categoria,
                'total': float(monto)
            })
        
        # Añadir datos al contexto
        context['pagos_socios'] = pagos_socios
        context['otros_ingresos'] = otros_ingresos
        context['egresos'] = egresos
        context['ingresos_por_categoria'] = ingresos_por_categoria
        context['egresos_por_categoria'] = egresos_por_categoria
        context['total_pagos_socios'] = total_pagos_socios
        
        return context


class InformeFinancieroCreateView(FinanzasRequiredMixin, CreateView):
    """Crea un nuevo informe financiero.
    Requiere permiso para acceder al módulo de finanzas."""
    model = InformeFinanciero
    form_class = InformeFinancieroForm
    template_name = 'finanzas/informe_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        
        # Predeterminar fechas para el mes actual
        hoy = timezone.now().date()
        primer_dia_mes = hoy.replace(day=1)
        
        initial['fecha_inicio'] = primer_dia_mes
        initial['fecha_fin'] = hoy
        initial['tipo_periodo'] = 'MENSUAL'
        initial['titulo'] = f"Informe Mensual {hoy.strftime('%B %Y')}"
        initial['creado_por'] = self.request.user.get_full_name() if hasattr(self.request.user, 'get_full_name') else self.request.user.username
        
        return initial
    
    def form_valid(self, form):
        informe = form.save(commit=False)
        
        # Generar automáticamente el informe
        informe.generar_informe()
        
        messages.success(self.request, "Informe financiero generado exitosamente")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('informe_detail', kwargs={'pk': self.object.pk})


class InformeFinancieroDeleteView(FinanzasRequiredMixin, DeleteView):
    """Elimina un informe financiero.
    Requiere permiso para acceder al módulo de finanzas."""
    model = InformeFinanciero
    template_name = 'finanzas/informe_confirm_delete.html'
    success_url = reverse_lazy('informe_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Informe eliminado exitosamente")
        return super().delete(request, *args, **kwargs)


@permiso_finanzas_required
def generar_informe_pdf(request, pk):
    """
    Genera un informe financiero en formato PDF.
    
    Esta función obtiene un informe existente y genera un archivo PDF con los datos.
    Requiere permiso para acceder al módulo de finanzas.
    
    Args:
        request: HttpRequest
        pk: ID del informe financiero
        
    Returns:
        HttpResponse: Respuesta con el archivo PDF
    """
    informe = get_object_or_404(InformeFinanciero, pk=pk)
    
    # En una implementación real, aquí se generaría el PDF con reportlab o weasyprint
    # Por ahora, solo redireccionamos al detalle del informe con un mensaje
    messages.info(request, "La funcionalidad de exportación a PDF está en desarrollo. Por favor, utilice la vista de detalle para ver el informe.")
    return redirect('informe_detail', pk=informe.pk)


# Vista de resumen financiero (Dashboard)
class DashboardFinancieroView(FinanzasRequiredMixin, TemplateView):
    """
    Muestra un panel de control con resumen financiero,
    gráficos y estadísticas importantes.
    Requiere permiso para acceder al módulo de finanzas.
    """
    template_name = 'finanzas/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener fechas para filtros (predeterminado: último mes)
        fecha_fin = timezone.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        # Permitir al usuario cambiar el rango de fechas
        if 'fecha_inicio' in self.request.GET and self.request.GET['fecha_inicio']:
            try:
                fecha_inicio = datetime.strptime(self.request.GET['fecha_inicio'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if 'fecha_fin' in self.request.GET and self.request.GET['fecha_fin']:
            try:
                fecha_fin = datetime.strptime(self.request.GET['fecha_fin'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Calcular totales para el período
        pagos_socios = PagoSocio.objects.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin)
        otros_ingresos = Ingreso.objects.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin)
        egresos = Egreso.objects.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin)
        
        total_pagos_socios = pagos_socios.aggregate(total=Sum('monto'))['total'] or 0
        total_otros_ingresos = otros_ingresos.aggregate(total=Sum('monto'))['total'] or 0
        total_ingresos = total_pagos_socios + total_otros_ingresos
        total_egresos = egresos.aggregate(total=Sum('monto'))['total'] or 0
        saldo = total_ingresos - total_egresos
        
        # Datos para gráficos
        ingresos_por_categoria = list(otros_ingresos.values('categoria__nombre')
                                    .annotate(total=Sum('monto'))
                                    .order_by('-total'))
        
        # Añadir cuotas de socios si hay
        if total_pagos_socios > 0:
            ingresos_por_categoria.append({
                'categoria__nombre': 'Cuotas de Socios',
                'total': total_pagos_socios
            })
        
        egresos_por_categoria = list(egresos.values('categoria__nombre')
                                   .annotate(total=Sum('monto'))
                                   .order_by('-total'))
        
        # Ingresos y egresos por mes (para gráfico de tendencia)
        # Últimos 6 meses
        fecha_inicio_tendencia = fecha_fin - timedelta(days=180)
        
        ingresos_por_mes = list(PagoSocio.objects.filter(fecha__gte=fecha_inicio_tendencia)
                              .annotate(mes=TruncMonth('fecha'))
                              .values('mes')
                              .annotate(total=Sum('monto'))
                              .order_by('mes'))
        
        otros_ingresos_por_mes = list(Ingreso.objects.filter(fecha__gte=fecha_inicio_tendencia)
                                    .annotate(mes=TruncMonth('fecha'))
                                    .values('mes')
                                    .annotate(total=Sum('monto'))
                                    .order_by('mes'))
        
        egresos_por_mes = list(Egreso.objects.filter(fecha__gte=fecha_inicio_tendencia)
                             .annotate(mes=TruncMonth('fecha'))
                             .values('mes')
                             .annotate(total=Sum('monto'))
                             .order_by('mes'))
        
        # Preparar datos para gráfico de tendencia
        meses = []
        datos_ingresos = []
        datos_egresos = []
        
        # Crear diccionarios para búsqueda rápida
        map_ingresos_cuotas = {item['mes'].strftime('%Y-%m'): item['total'] for item in ingresos_por_mes}
        map_ingresos_otros = {item['mes'].strftime('%Y-%m'): item['total'] for item in otros_ingresos_por_mes}
        map_egresos = {item['mes'].strftime('%Y-%m'): item['total'] for item in egresos_por_mes}
        
        # Generar datos para los últimos 6 meses
        for i in range(6):
            fecha = fecha_fin - timedelta(days=i*30)
            mes_key = fecha.strftime('%Y-%m')
            nombre_mes = fecha.strftime('%b %Y')
            
            meses.append(nombre_mes)
            
            # Sumar ingresos de cuotas y otros ingresos
            ingreso_cuota = map_ingresos_cuotas.get(mes_key, 0)
            ingreso_otro = map_ingresos_otros.get(mes_key, 0)
            datos_ingresos.append(float(ingreso_cuota + ingreso_otro))
            
            # Egresos
            datos_egresos.append(float(map_egresos.get(mes_key, 0)))
        
        # Revertir listas para mostrar en orden cronológico
        meses.reverse()
        datos_ingresos.reverse()
        datos_egresos.reverse()
        
        # Datos sobre socios
        total_socios = Socio.objects.count()
        socios_activos = Socio.objects.filter(estado='ACTIVO').count()
        
        # Lista de socios con pagos atrasados
        socios_atrasados = []
        for socio in Socio.objects.filter(estado='ACTIVO'):
            if not socio.esta_al_dia():
                socios_atrasados.append({
                    'socio': socio,
                    'ultima_fecha': socio.get_ultima_cuota()
                })
        
        context.update({
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'total_pagos_socios': total_pagos_socios,
            'total_otros_ingresos': total_otros_ingresos,
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'saldo': saldo,
            'ingresos_por_categoria': ingresos_por_categoria,
            'egresos_por_categoria': egresos_por_categoria,
            'meses': meses,
            'datos_ingresos': datos_ingresos,
            'datos_egresos': datos_egresos,
            'total_socios': total_socios,
            'socios_activos': socios_activos,
            'socios_atrasados': socios_atrasados
        })
        
        return context
