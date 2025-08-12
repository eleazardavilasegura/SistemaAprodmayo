from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q, Count, Avg
from django.utils import timezone

import json
import datetime

# Importar mixins y decoradores de permisos
from usuarios.decorators import TalleresRequiredMixin, permiso_talleres_required

from .models import Taller, Participante, Asistencia, Evaluacion, Material
from .forms import (
    TallerForm, ParticipanteForm, AsistenciaForm,
    AsistenciaMasivaForm, EvaluacionForm, MaterialForm
)
from beneficiarias.models import Beneficiaria


class TallerListView(TalleresRequiredMixin, ListView):
    """
    Vista para mostrar la lista de talleres.
    
    Muestra todos los talleres disponibles con opciones de filtrado.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Taller
    template_name = 'talleres/taller_list.html'
    context_object_name = 'talleres'
    paginate_by = 10  # Paginación cada 10 elementos
    
    def get_queryset(self):
        """
        Personaliza el conjunto de resultados según los filtros aplicados.
        
        Returns:
            QuerySet: Talleres filtrados según los parámetros de búsqueda
        """
        # Actualizar automáticamente los estados de los talleres
        self.actualizar_estados_talleres()
        
        queryset = Taller.objects.all()
        
        # Filtrar por estado
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
            
        # Filtrar por período (fecha)
        periodo = self.request.GET.get('periodo')
        hoy = timezone.now().date()
        if periodo == 'actual':
            queryset = queryset.filter(fecha_inicio__lte=hoy, fecha_fin__gte=hoy)
        elif periodo == 'proximo':
            queryset = queryset.filter(fecha_inicio__gt=hoy)
        elif periodo == 'finalizado':
            queryset = queryset.filter(fecha_fin__lt=hoy)
        
        # Búsqueda por término
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(descripcion__icontains=q) |
                Q(facilitador__icontains=q) |
                Q(lugar__icontains=q)
            )
            
        return queryset
        
    def actualizar_estados_talleres(self):
        """
        Actualiza el estado de los talleres según sus fechas
        """
        # Obtener fecha actual
        hoy = timezone.now().date()
        
        # Obtener todos los talleres que no están cancelados
        talleres = Taller.objects.exclude(estado='CANCELADO')
        
        # Verificar y actualizar el estado de cada taller
        for taller in talleres:
            nuevo_estado = None
            
            # Determinar el nuevo estado basado en las fechas
            if hoy < taller.fecha_inicio:
                nuevo_estado = 'PROGRAMADO'
            elif hoy <= taller.fecha_fin:
                nuevo_estado = 'EN_CURSO'
            else:
                nuevo_estado = 'FINALIZADO'
            
            # Actualizar el estado si ha cambiado
            if taller.estado != nuevo_estado:
                taller.estado = nuevo_estado
                taller.save(update_fields=['estado'])
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        
        # Estadísticas de talleres
        hoy = timezone.now().date()
        context['total_talleres'] = Taller.objects.count()
        context['talleres_activos'] = Taller.objects.filter(fecha_inicio__lte=hoy, fecha_fin__gte=hoy).count()
        context['talleres_proximos'] = Taller.objects.filter(fecha_inicio__gt=hoy).count()
        context['talleres_finalizados'] = Taller.objects.filter(fecha_fin__lt=hoy).count()
        
        # Mantener parámetros de filtro en la paginación
        context['current_filters'] = '&'.join([
            f"{key}={value}"
            for key, value in self.request.GET.items()
            if key != 'page'
        ])
        
        return context


class TallerCreateView(TalleresRequiredMixin, CreateView):
    """
    Vista para crear un nuevo taller.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Taller
    form_class = TallerForm
    template_name = 'talleres/taller_form.html'
    success_url = reverse_lazy('taller_list')
    
    def form_valid(self, form):
        """
        Procesa el formulario si es válido.
        Asigna el estado según las fechas automáticamente.
        
        Args:
            form: Formulario validado
            
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        taller = form.instance
        
        # Obtener fecha actual
        hoy = timezone.now().date()
        
        # Determinar el estado inicial basado en las fechas
        if form.cleaned_data.get('estado') != 'CANCELADO':
            if hoy < taller.fecha_inicio:
                taller.estado = 'PROGRAMADO'
            elif hoy <= taller.fecha_fin:
                taller.estado = 'EN_CURSO'
            else:
                taller.estado = 'FINALIZADO'
        
        messages.success(self.request, 'Taller creado exitosamente.')
        return super().form_valid(form)


class TallerDetailView(TalleresRequiredMixin, DetailView):
    """
    Vista para mostrar detalles de un taller.
    
    Incluye información sobre participantes, materiales y asistencia.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Taller
    template_name = 'talleres/taller_detail.html'
    context_object_name = 'taller'
    
    def get_object(self, queryset=None):
        """
        Recupera el objeto taller y actualiza su estado según las fechas.
        """
        taller = super().get_object(queryset)
        
        # No actualizar talleres cancelados
        if taller.estado != 'CANCELADO':
            # Obtener fecha actual
            hoy = timezone.now().date()
            
            # Determinar el estado correcto basado en las fechas
            if hoy < taller.fecha_inicio:
                nuevo_estado = 'PROGRAMADO'
            elif hoy <= taller.fecha_fin:
                nuevo_estado = 'EN_CURSO'
            else:
                nuevo_estado = 'FINALIZADO'
            
            # Actualizar el estado si ha cambiado
            if taller.estado != nuevo_estado:
                taller.estado = nuevo_estado
                taller.save(update_fields=['estado'])
                
        return taller
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        taller = self.object
        
        # Obtener participantes
        context['participantes'] = taller.participante_set.all()
        context['total_participantes'] = taller.participante_set.count()
        context['disponibilidad'] = taller.disponibilidad()
        
        # Calcular ocupación
        context['porcentaje_ocupacion'] = taller.porcentaje_ocupacion()
        
        # Obtener materiales
        context['materiales'] = taller.material_set.all().order_by('-fecha_creacion')
        
        # Calcular estadísticas de asistencia
        total_sesiones = (taller.fecha_fin - taller.fecha_inicio).days + 1
        context['total_sesiones'] = total_sesiones
        
        # Comprobar si es un taller actual o pasado
        hoy = timezone.now().date()
        context['es_taller_actual'] = taller.fecha_inicio <= hoy <= taller.fecha_fin
        context['es_taller_pasado'] = taller.fecha_fin < hoy
        context['es_taller_futuro'] = taller.fecha_inicio > hoy
        
        # Fechas del taller como lista para el registro de asistencia
        fechas_taller = []
        fecha_actual = taller.fecha_inicio
        while fecha_actual <= taller.fecha_fin:
            # Solo incluir días de semana (excluir sábados y domingos)
            if fecha_actual.weekday() < 5:  # 0=Lunes, 6=Domingo
                fechas_taller.append(fecha_actual)
            fecha_actual += datetime.timedelta(days=1)
        
        context['fechas_taller'] = fechas_taller
        
        return context


class TallerUpdateView(TalleresRequiredMixin, UpdateView):
    """
    Vista para actualizar un taller existente.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Taller
    form_class = TallerForm
    template_name = 'talleres/taller_form.html'
    
    def form_valid(self, form):
        """
        Procesa el formulario si es válido.
        Asigna el estado según las fechas automáticamente.
        
        Args:
            form: Formulario validado
            
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        taller = form.instance
        
        # Obtener fecha actual
        hoy = timezone.now().date()
        
        # Solo actualizar el estado si no está cancelado
        if form.cleaned_data.get('estado') != 'CANCELADO':
            # Determinar el estado basado en las fechas
            if hoy < taller.fecha_inicio:
                taller.estado = 'PROGRAMADO'
            elif hoy <= taller.fecha_fin:
                taller.estado = 'EN_CURSO'
            else:
                taller.estado = 'FINALIZADO'
                
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Determina la URL a la que redireccionar después del éxito.
        
        Returns:
            str: URL de redirección
        """
        messages.success(self.request, 'Taller actualizado exitosamente.')
        return reverse('taller_detail', kwargs={'pk': self.object.pk})


class TallerDeleteView(TalleresRequiredMixin, DeleteView):
    """
    Vista para eliminar un taller.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Taller
    template_name = 'talleres/confirm_delete.html'
    success_url = reverse_lazy('taller_list')
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['object_name'] = 'el taller'
        context['cancel_url'] = reverse('taller_detail', kwargs={'pk': self.object.pk})
        
        # Mensaje de advertencia si hay participantes registrados
        participantes_count = self.object.participante_set.count()
        if participantes_count > 0:
            context['extra_message'] = (
                f"Este taller tiene {participantes_count} participantes registrados. "
                "Al eliminar el taller, también se eliminarán todos los registros de participantes, "
                "asistencias y evaluaciones asociados."
            )
        
        return context
    
    def delete(self, request, *args, **kwargs):
        """
        Elimina el taller y muestra un mensaje de éxito.
        
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        messages.success(request, 'El taller ha sido eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class ParticipanteListView(TalleresRequiredMixin, ListView):
    """
    Vista para mostrar la lista de participantes de un taller.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Participante
    template_name = 'talleres/participante_list.html'
    context_object_name = 'participantes'
    paginate_by = 20  # Paginación cada 20 elementos
    
    def get_queryset(self):
        """
        Personaliza el conjunto de resultados para mostrar solo los
        participantes del taller seleccionado.
        
        Returns:
            QuerySet: Participantes filtrados según el taller y parámetros de búsqueda
        """
        self.taller = get_object_or_404(Taller, pk=self.kwargs['taller_id'])
        queryset = Participante.objects.filter(taller=self.taller)
        
        # Filtrar por estado
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Búsqueda por término
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nombres__icontains=q) |
                Q(apellidos__icontains=q) |
                Q(dni__icontains=q) |
                Q(beneficiaria__nombres__icontains=q) |
                Q(beneficiaria__apellidos__icontains=q) |
                Q(beneficiaria__dni__icontains=q)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['taller'] = self.taller
        
        # Estadísticas de participantes
        context['total_participantes'] = self.taller.participante_set.count()
        context['capacidad'] = self.taller.capacidad
        context['disponibilidad'] = self.taller.disponibilidad()
        
        return context


@permiso_talleres_required
def buscar_beneficiarias(request):
    """
    Vista para buscar beneficiarias mediante AJAX.
    
    Permite buscar beneficiarias por nombre, apellido o DNI para
    vincularlas a un participante.
    Requiere permiso para acceder al módulo de talleres.
    
    Args:
        request: HttpRequest con parámetro 'term' para el término de búsqueda
        
    Returns:
        JsonResponse: Lista de beneficiarias que coinciden con el término de búsqueda
    """
    term = request.GET.get('term', '')
    if not term or len(term) < 3:
        return JsonResponse([], safe=False)
    
    # Buscar beneficiarias que coincidan con el término
    beneficiarias = Beneficiaria.objects.filter(
        Q(nombres__icontains=term) |
        Q(apellidos__icontains=term) |
        Q(dni__icontains=term)
    )[:10]  # Limitar a 10 resultados
    
    # Formatear los resultados
    results = []
    for beneficiaria in beneficiarias:
        results.append({
            'id': beneficiaria.id,
            'label': f"{beneficiaria.nombres} {beneficiaria.apellidos} (DNI: {beneficiaria.dni})",
            'value': beneficiaria.id,
            'nombres': beneficiaria.nombres,
            'apellidos': beneficiaria.apellidos,
            'dni': beneficiaria.dni,
            'telefono': beneficiaria.telefono,
            'email': beneficiaria.email if hasattr(beneficiaria, 'email') else ''
        })
    
    return JsonResponse(results, safe=False)


class ParticipanteCreateView(TalleresRequiredMixin, CreateView):
    """
    Vista para inscribir un nuevo participante en un taller.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Participante
    form_class = ParticipanteForm
    template_name = 'talleres/participante_form.html'
    
    def get_form_kwargs(self):
        """
        Proporciona argumentos adicionales al formulario.
        
        Returns:
            dict: Argumentos para inicializar el formulario
        """
        kwargs = super().get_form_kwargs()
        kwargs['taller_id'] = self.kwargs['taller_id']
        return kwargs
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['taller'] = get_object_or_404(Taller, pk=self.kwargs['taller_id'])
        return context
    
    def form_valid(self, form):
        """
        Procesa el formulario si es válido.
        
        Args:
            form: Formulario validado
            
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        try:
            # Imprimir contenido del formulario para depuración
            print("Datos del formulario:", form.cleaned_data)
            
            # Obtener el taller
            taller_id = self.kwargs['taller_id']
            print(f"ID del taller: {taller_id}")
            taller = get_object_or_404(Taller, pk=taller_id)
            print(f"Taller encontrado: {taller.nombre}")
            
            # Verificar si el taller permite inscripciones (solo si está PROGRAMADO o EN_CURSO)
            if taller.estado not in ['PROGRAMADO', 'EN_CURSO']:
                messages.error(self.request, f'No es posible registrar participantes. El taller está {taller.get_estado_display()}.')
                return self.form_invalid(form)
            
            # No verificamos si el taller está lleno, permitimos inscribir más participantes de la capacidad
            
            # Crear el objeto participante sin guardarlo aún
            participante = form.save(commit=False)
            participante.taller = taller
            
            # Asignar fecha de inscripción si no tiene
            participante.fecha_inscripcion = timezone.now().date()
            
            # Asignar estado CONFIRMADO siempre
            participante.estado = 'CONFIRMADO'
            
            # Mostrar información detallada del participante
            print(f"Datos del participante a guardar:")
            print(f"Nombres: {participante.nombres}")
            print(f"Apellidos: {participante.apellidos}")
            print(f"DNI: {participante.dni}")
            print(f"Teléfono: {participante.telefono}")
            print(f"Email: {participante.email}")
            print(f"Taller ID: {participante.taller.id}")
            print(f"Estado: {participante.estado}")
            
            # Guardar el participante
            participante.save()
            print(f"Participante guardado con ID: {participante.id}")
            
            # Agregar mensaje de éxito
            messages.success(self.request, '¡PARTICIPANTE REGISTRADO EXITOSAMENTE!')
            
            # Guardar el objeto en self.object para que CreateView funcione correctamente
            self.object = participante
            
            # Redireccionar al listado de participantes
            return HttpResponseRedirect(self.get_success_url())
            
        except Exception as e:
            import traceback
            print(f"Error al guardar participante: {str(e)}")
            print(traceback.format_exc())  # Imprime el stack trace completo
            messages.error(self.request, f'Error al registrar el participante: {str(e)}')
            return self.form_invalid(form)
    
    def get_success_url(self):
        """
        Retorna la URL a la que redireccionar después de un registro exitoso.
        
        Returns:
            str: URL de redirección
        """
        print("Redireccionando a la lista de participantes")
        return reverse('participante_list', kwargs={'taller_id': self.kwargs['taller_id']})
    
    def get_success_url(self):
        """
        Determina la URL a la que redireccionar después del éxito.
        
        Returns:
            str: URL de redirección
        """
        return reverse('participante_list', kwargs={'taller_id': self.kwargs['taller_id']})


class ParticipanteDetailView(TalleresRequiredMixin, DetailView):
    """
    Vista para mostrar detalles de un participante.
    
    Incluye información sobre asistencia, evaluaciones y otra información personal.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Participante
    template_name = 'talleres/participante_detail.html'
    context_object_name = 'participante'
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        participante = self.object
        
        # Obtener registros de asistencia
        context['asistencias'] = Asistencia.objects.filter(participante=participante).order_by('-fecha')
        
        # Calcular estadísticas de asistencia
        total_asistencias = context['asistencias'].filter(estado='PRESENTE').count()
        total_tardanzas = context['asistencias'].filter(estado='TARDANZA').count()
        total_ausencias = context['asistencias'].filter(estado='AUSENTE').count()
        total_justificadas = context['asistencias'].filter(estado='JUSTIFICADO').count()
        total_sesiones = context['asistencias'].count()
        
        context['total_asistencias'] = total_asistencias
        context['total_tardanzas'] = total_tardanzas
        context['total_ausencias'] = total_ausencias
        context['total_justificadas'] = total_justificadas
        context['total_sesiones'] = total_sesiones
        
        if total_sesiones > 0:
            context['porcentaje_asistencia'] = (total_asistencias / total_sesiones) * 100
        else:
            context['porcentaje_asistencia'] = 0
        
        # Obtener evaluaciones
        context['evaluaciones'] = Evaluacion.objects.filter(participante=participante).order_by('-fecha')
        
        # Calcular promedio de calificaciones
        calificaciones = [ev.calificacion for ev in context['evaluaciones'] if ev.calificacion is not None]
        if calificaciones:
            context['promedio_calificaciones'] = sum(calificaciones) / len(calificaciones)
        else:
            context['promedio_calificaciones'] = None
        
        return context


class ParticipanteUpdateView(TalleresRequiredMixin, UpdateView):
    """
    Vista para actualizar la información de un participante.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Participante
    form_class = ParticipanteForm
    template_name = 'talleres/participante_form.html'
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['taller'] = self.object.taller
        return context
    
    def form_valid(self, form):
        """
        Procesa el formulario si es válido.
        
        Args:
            form: Formulario validado
            
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        messages.success(self.request, 'Información del participante actualizada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Determina la URL a la que redireccionar después del éxito.
        
        Returns:
            str: URL de redirección
        """
        return reverse('participante_detail', kwargs={'pk': self.object.pk})


class ParticipanteDeleteView(TalleresRequiredMixin, DeleteView):
    """
    Vista para eliminar un participante.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Participante
    template_name = 'talleres/confirm_delete.html'
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['object_name'] = 'el participante'
        context['cancel_url'] = reverse('participante_detail', kwargs={'pk': self.object.pk})
        
        # Mensaje de advertencia si hay asistencias o evaluaciones
        asistencias_count = Asistencia.objects.filter(participante=self.object).count()
        evaluaciones_count = Evaluacion.objects.filter(participante=self.object).count()
        
        warnings = []
        if asistencias_count > 0:
            warnings.append(f"Se eliminarán {asistencias_count} registros de asistencia.")
        if evaluaciones_count > 0:
            warnings.append(f"Se eliminarán {evaluaciones_count} evaluaciones.")
        
        if warnings:
            context['extra_message'] = " ".join(warnings)
        
        return context
    
    def delete(self, request, *args, **kwargs):
        """
        Elimina el participante y muestra un mensaje de éxito.
        
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        taller_id = self.get_object().taller.id
        messages.success(request, 'El participante ha sido eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        """
        Determina la URL a la que redireccionar después del éxito.
        
        Returns:
            str: URL de redirección
        """
        return reverse('participante_list', kwargs={'taller_id': self.object.taller.id})


class AsistenciaListView(TalleresRequiredMixin, ListView):
    """
    Vista para mostrar la lista de asistencias de un taller.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Asistencia
    template_name = 'talleres/asistencia_list.html'
    context_object_name = 'asistencias'
    paginate_by = 30  # Paginación cada 30 elementos
    
    def get_queryset(self):
        """
        Personaliza el conjunto de resultados para mostrar solo las
        asistencias del taller seleccionado.
        
        Returns:
            QuerySet: Asistencias filtradas según el taller y parámetros de búsqueda
        """
        self.taller = get_object_or_404(Taller, pk=self.kwargs['taller_id'])
        queryset = Asistencia.objects.filter(participante__taller=self.taller)
        
        # Filtrar por fecha
        fecha = self.request.GET.get('fecha')
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        
        # Filtrar por estado
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por participante
        participante_id = self.request.GET.get('participante')
        if participante_id:
            queryset = queryset.filter(participante_id=participante_id)
        
        # Ordenar por fecha y participante
        queryset = queryset.order_by('-fecha', 'participante__apellidos', 'participante__nombres')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['taller'] = self.taller
        
        # Lista de participantes para el filtro
        context['participantes'] = Participante.objects.filter(taller=self.taller)
        
        # Fechas únicas de asistencia para el filtro
        context['fechas'] = Asistencia.objects.filter(
            participante__taller=self.taller
        ).values_list('fecha', flat=True).distinct().order_by('-fecha')
        
        return context


@permiso_talleres_required
def asistencia_masiva(request, taller_id):
    """
    Vista para registrar asistencia masiva de participantes.
    
    Permite registrar la asistencia de todos los participantes de un taller
    en una sola operación.
    Requiere permiso para acceder al módulo de talleres.
    
    Args:
        request: HttpRequest
        taller_id: ID del taller
        
    Returns:
        HttpResponse: Renderización de la plantilla con el formulario o redirección
    """
    taller = get_object_or_404(Taller, pk=taller_id)
    participantes = Participante.objects.filter(taller=taller, estado='CONFIRMADO')
    
    if request.method == 'POST':
        form = AsistenciaMasivaForm(request.POST, participantes=participantes)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            registrado_por = form.cleaned_data['registrado_por']
            
            # Crear o actualizar registros de asistencia para cada participante
            for participante in participantes:
                estado = form.cleaned_data[f'estado_{participante.id}']
                observaciones = form.cleaned_data[f'observaciones_{participante.id}']
                
                # Buscar si ya existe un registro para este participante en esta fecha
                asistencia, created = Asistencia.objects.update_or_create(
                    participante=participante,
                    fecha=fecha,
                    defaults={
                        'estado': estado,
                        'observaciones': observaciones,
                        'registrado_por': registrado_por
                    }
                )
            
            messages.success(request, 'Registros de asistencia guardados exitosamente.')
            return redirect('asistencia_list', taller_id=taller.id)
    else:
        form = AsistenciaMasivaForm(participantes=participantes)
    
    return render(request, 'talleres/asistencia_masiva.html', {
        'form': form,
        'taller': taller,
        'participantes': participantes
    })


class AsistenciaCreateView(TalleresRequiredMixin, CreateView):
    """
    Vista para crear un nuevo registro de asistencia.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Asistencia
    form_class = AsistenciaForm
    template_name = 'talleres/asistencia_form.html'
    
    def get_form_kwargs(self):
        """
        Proporciona argumentos adicionales al formulario.
        
        Returns:
            dict: Argumentos para inicializar el formulario
        """
        kwargs = super().get_form_kwargs()
        kwargs['taller_id'] = self.kwargs['taller_id']
        return kwargs
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['taller'] = get_object_or_404(Taller, pk=self.kwargs['taller_id'])
        return context
    
    def form_valid(self, form):
        """
        Procesa el formulario si es válido.
        
        Args:
            form: Formulario validado
            
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        messages.success(self.request, 'Registro de asistencia creado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Determina la URL a la que redireccionar después del éxito.
        
        Returns:
            str: URL de redirección
        """
        return reverse('asistencia_list', kwargs={'taller_id': self.kwargs['taller_id']})


class AsistenciaUpdateView(TalleresRequiredMixin, UpdateView):
    """
    Vista para actualizar un registro de asistencia.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Asistencia
    form_class = AsistenciaForm
    template_name = 'talleres/asistencia_form.html'
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['taller'] = self.object.participante.taller
        return context
    
    def form_valid(self, form):
        """
        Procesa el formulario si es válido.
        
        Args:
            form: Formulario validado
            
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        messages.success(self.request, 'Registro de asistencia actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Determina la URL a la que redireccionar después del éxito.
        
        Returns:
            str: URL de redirección
        """
        return reverse('asistencia_list', kwargs={'taller_id': self.object.participante.taller.id})


class AsistenciaDeleteView(TalleresRequiredMixin, DeleteView):
    """
    Vista para eliminar un registro de asistencia.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Asistencia
    template_name = 'talleres/confirm_delete.html'
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['object_name'] = 'el registro de asistencia'
        context['cancel_url'] = reverse('asistencia_list', kwargs={'taller_id': self.object.participante.taller.id})
        return context
    
    def delete(self, request, *args, **kwargs):
        """
        Elimina el registro de asistencia y muestra un mensaje de éxito.
        
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        taller_id = self.get_object().participante.taller.id
        messages.success(request, 'El registro de asistencia ha sido eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        """
        Determina la URL a la que redireccionar después del éxito.
        
        Returns:
            str: URL de redirección
        """
        return reverse('asistencia_list', kwargs={'taller_id': self.object.participante.taller.id})


class EvaluacionListView(TalleresRequiredMixin, ListView):
    """
    Vista para mostrar la lista de evaluaciones de un taller.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Evaluacion
    template_name = 'talleres/evaluacion_list.html'
    context_object_name = 'evaluaciones'
    paginate_by = 20  # Paginación cada 20 elementos
    
    def get_queryset(self):
        """
        Personaliza el conjunto de resultados para mostrar solo las
        evaluaciones del taller seleccionado.
        
        Returns:
            QuerySet: Evaluaciones filtradas según el taller y parámetros de búsqueda
        """
        self.taller = get_object_or_404(Taller, pk=self.kwargs['taller_id'])
        queryset = Evaluacion.objects.filter(participante__taller=self.taller)
        
        # Filtrar por fecha
        fecha = self.request.GET.get('fecha')
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        
        # Filtrar por nivel de logro
        nivel_logro = self.request.GET.get('nivel_logro')
        if nivel_logro:
            queryset = queryset.filter(nivel_logro=nivel_logro)
        
        # Filtrar por participante
        participante_id = self.request.GET.get('participante')
        if participante_id:
            queryset = queryset.filter(participante_id=participante_id)
        
        # Ordenar por fecha y participante
        queryset = queryset.order_by('-fecha', 'participante__apellidos', 'participante__nombres')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['taller'] = self.taller
        
        # Lista de participantes para el filtro
        context['participantes'] = Participante.objects.filter(taller=self.taller)
        
        # Fechas únicas de evaluación para el filtro
        context['fechas'] = Evaluacion.objects.filter(
            participante__taller=self.taller
        ).values_list('fecha', flat=True).distinct().order_by('-fecha')
        
        # Estadísticas de evaluaciones
        context['total_evaluaciones'] = self.get_queryset().count()
        
        # Promedio de calificaciones
        avg_calificacion = self.get_queryset().aggregate(Avg('calificacion'))['calificacion__avg']
        context['promedio_calificacion'] = avg_calificacion
        
        # Distribución de niveles de logro
        niveles_logro = self.get_queryset().values('nivel_logro').annotate(
            count=Count('nivel_logro')
        ).order_by('nivel_logro')
        
        context['niveles_logro'] = {}
        for nivel in niveles_logro:
            nivel_nombre = dict(Evaluacion.LOGRO_CHOICES).get(nivel['nivel_logro'], nivel['nivel_logro'])
            context['niveles_logro'][nivel_nombre] = nivel['count']
        
        return context


class EvaluacionCreateView(TalleresRequiredMixin, CreateView):
    """
    Vista para crear una nueva evaluación.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Evaluacion
    form_class = EvaluacionForm
    template_name = 'talleres/evaluacion_form.html'
    
    def get_form_kwargs(self):
        """
        Proporciona argumentos adicionales al formulario.
        
        Returns:
            dict: Argumentos para inicializar el formulario
        """
        kwargs = super().get_form_kwargs()
        kwargs['taller_id'] = self.kwargs['taller_id']
        return kwargs
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['taller'] = get_object_or_404(Taller, pk=self.kwargs['taller_id'])
        return context
    
    def form_valid(self, form):
        """
        Procesa el formulario si es válido.
        
        Args:
            form: Formulario validado
            
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        messages.success(self.request, 'Evaluación registrada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Determina la URL a la que redireccionar después del éxito.
        
        Returns:
            str: URL de redirección
        """
        return reverse('evaluacion_list', kwargs={'taller_id': self.kwargs['taller_id']})


class EvaluacionDetailView(TalleresRequiredMixin, DetailView):
    """
    Vista para mostrar detalles de una evaluación.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Evaluacion
    template_name = 'talleres/evaluacion_detail.html'
    context_object_name = 'evaluacion'


class EvaluacionUpdateView(TalleresRequiredMixin, UpdateView):
    """
    Vista para actualizar una evaluación.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Evaluacion
    form_class = EvaluacionForm
    template_name = 'talleres/evaluacion_form.html'
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['taller'] = self.object.participante.taller
        return context
    
    def form_valid(self, form):
        """
        Procesa el formulario si es válido.
        
        Args:
            form: Formulario validado
            
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        messages.success(self.request, 'Evaluación actualizada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Determina la URL a la que redireccionar después del éxito.
        
        Returns:
            str: URL de redirección
        """
        return reverse('evaluacion_detail', kwargs={'pk': self.object.pk})


class EvaluacionDeleteView(TalleresRequiredMixin, DeleteView):
    """
    Vista para eliminar una evaluación.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Evaluacion
    template_name = 'talleres/confirm_delete.html'
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['object_name'] = 'la evaluación'
        context['cancel_url'] = reverse('evaluacion_detail', kwargs={'pk': self.object.pk})
        return context
    
    def delete(self, request, *args, **kwargs):
        """
        Elimina la evaluación y muestra un mensaje de éxito.
        
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        taller_id = self.get_object().participante.taller.id
        messages.success(request, 'La evaluación ha sido eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        """
        Determina la URL a la que redireccionar después del éxito.
        
        Returns:
            str: URL de redirección
        """
        return reverse('evaluacion_list', kwargs={'taller_id': self.object.participante.taller.id})


class MaterialListView(TalleresRequiredMixin, ListView):
    """
    Vista para mostrar la lista de materiales de un taller.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Material
    template_name = 'talleres/material_list.html'
    context_object_name = 'materiales'
    paginate_by = 20  # Paginación cada 20 elementos
    
    def get_queryset(self):
        """
        Personaliza el conjunto de resultados para mostrar solo los
        materiales del taller seleccionado.
        
        Returns:
            QuerySet: Materiales filtrados según el taller y parámetros de búsqueda
        """
        self.taller = get_object_or_404(Taller, pk=self.kwargs['taller_id'])
        queryset = Material.objects.filter(taller=self.taller)
        
        # Filtrar por tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Búsqueda por término
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(titulo__icontains=q) |
                Q(descripcion__icontains=q) |
                Q(autor__icontains=q)
            )
        
        # Ordenar por fecha de creación
        queryset = queryset.order_by('-fecha_creacion')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['taller'] = self.taller
        
        # Conteo por tipo de material para mostrar estadísticas
        context['tipos_count'] = Material.objects.filter(
            taller=self.taller
        ).values('tipo').annotate(count=Count('tipo'))
        
        return context


class MaterialCreateView(TalleresRequiredMixin, CreateView):
    """
    Vista para agregar un nuevo material a un taller.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Material
    form_class = MaterialForm
    template_name = 'talleres/material_form.html'
    
    def get_form_kwargs(self):
        """
        Proporciona argumentos adicionales al formulario.
        
        Returns:
            dict: Argumentos para inicializar el formulario
        """
        kwargs = super().get_form_kwargs()
        kwargs['taller_id'] = self.kwargs['taller_id']
        return kwargs
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['taller'] = get_object_or_404(Taller, pk=self.kwargs['taller_id'])
        return context
    
    def form_valid(self, form):
        """
        Procesa el formulario si es válido.
        
        Args:
            form: Formulario validado
            
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        # Asignar el taller al material
        form.instance.taller_id = self.kwargs['taller_id']
        
        messages.success(self.request, 'Material agregado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Determina la URL a la que redireccionar después del éxito.
        
        Returns:
            str: URL de redirección
        """
        return reverse('material_list', kwargs={'taller_id': self.kwargs['taller_id']})


class MaterialDetailView(TalleresRequiredMixin, DetailView):
    """
    Vista para mostrar detalles de un material.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Material
    template_name = 'talleres/material_detail.html'
    context_object_name = 'material'


class MaterialUpdateView(TalleresRequiredMixin, UpdateView):
    """
    Vista para actualizar un material.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Material
    form_class = MaterialForm
    template_name = 'talleres/material_form.html'
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['taller'] = self.object.taller
        return context
    
    def form_valid(self, form):
        """
        Procesa el formulario si es válido.
        
        Args:
            form: Formulario validado
            
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        messages.success(self.request, 'Material actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Determina la URL a la que redireccionar después del éxito.
        
        Returns:
            str: URL de redirección
        """
        return reverse('material_detail', kwargs={'pk': self.object.pk})


class MaterialDeleteView(TalleresRequiredMixin, DeleteView):
    """
    Vista para eliminar un material.
    Requiere permiso para acceder al módulo de talleres.
    """
    model = Material
    template_name = 'talleres/confirm_delete.html'
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional a la plantilla.
        
        Returns:
            dict: Contexto con variables adicionales
        """
        context = super().get_context_data(**kwargs)
        context['object_name'] = 'el material'
        context['cancel_url'] = reverse('material_detail', kwargs={'pk': self.object.pk})
        return context
    
    def delete(self, request, *args, **kwargs):
        """
        Elimina el material y muestra un mensaje de éxito.
        
        Returns:
            HttpResponse: Redirección a la página de éxito
        """
        taller_id = self.get_object().taller.id
        messages.success(request, 'El material ha sido eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        """
        Determina la URL a la que redireccionar después del éxito.
        
        Returns:
            str: URL de redirección
        """
        return reverse('material_list', kwargs={'taller_id': self.object.taller.id})


@permiso_talleres_required
def reporte_asistencia(request, taller_id):
    """
    Vista para generar un reporte de asistencia.
    
    Muestra un informe detallado de la asistencia de los participantes
    del taller a lo largo del tiempo.
    Requiere permiso para acceder al módulo de talleres.
    
    Args:
        request: HttpRequest
        taller_id: ID del taller
        
    Returns:
        HttpResponse: Renderización de la plantilla con el reporte
    """
    taller = get_object_or_404(Taller, pk=taller_id)
    participantes = Participante.objects.filter(taller=taller, estado='CONFIRMADO')
    
    # Obtener todas las fechas en las que se ha registrado asistencia para este taller
    fechas = Asistencia.objects.filter(
        participante__taller=taller
    ).values_list('fecha', flat=True).distinct().order_by('fecha')
    
    # Crear matriz de asistencia
    matriz_asistencia = []
    for participante in participantes:
        fila = {
            'participante': participante,
            'asistencias': []
        }
        
        total_presente = 0
        total_tardanza = 0
        total_ausente = 0
        total_justificado = 0
        
        for fecha in fechas:
            try:
                asistencia = Asistencia.objects.get(participante=participante, fecha=fecha)
                fila['asistencias'].append(asistencia)
                
                # Contabilizar por tipo
                if asistencia.estado == 'PRESENTE':
                    total_presente += 1
                elif asistencia.estado == 'TARDANZA':
                    total_tardanza += 1
                elif asistencia.estado == 'AUSENTE':
                    total_ausente += 1
                elif asistencia.estado == 'JUSTIFICADO':
                    total_justificado += 1
                
            except Asistencia.DoesNotExist:
                fila['asistencias'].append(None)
        
        # Calcular totales y porcentajes
        total_registros = len([a for a in fila['asistencias'] if a is not None])
        fila['total_presente'] = total_presente
        fila['total_tardanza'] = total_tardanza
        fila['total_ausente'] = total_ausente
        fila['total_justificado'] = total_justificado
        fila['total_registros'] = total_registros
        
        if total_registros > 0:
            fila['porcentaje_asistencia'] = ((total_presente + total_tardanza) / total_registros) * 100
        else:
            fila['porcentaje_asistencia'] = 0
        
        matriz_asistencia.append(fila)
    
    return render(request, 'talleres/reporte_asistencia.html', {
        'taller': taller,
        'fechas': fechas,
        'matriz_asistencia': matriz_asistencia
    })


@permiso_talleres_required
def reporte_evaluaciones(request, taller_id):
    """
    Vista para generar un reporte de evaluaciones.
    
    Muestra un informe detallado de las evaluaciones de los participantes
    del taller.
    Requiere permiso para acceder al módulo de talleres.
    
    Args:
        request: HttpRequest
        taller_id: ID del taller
        
    Returns:
        HttpResponse: Renderización de la plantilla con el reporte
    """
    taller = get_object_or_404(Taller, pk=taller_id)
    participantes = Participante.objects.filter(taller=taller, estado='CONFIRMADO')
    
    # Obtener todas las evaluaciones para este taller
    evaluaciones = Evaluacion.objects.filter(
        participante__taller=taller
    ).order_by('participante', 'fecha')
    
    # Crear un diccionario de evaluaciones por participante
    evaluaciones_por_participante = {}
    for participante in participantes:
        evaluaciones_por_participante[participante.id] = {
            'participante': participante,
            'evaluaciones': evaluaciones.filter(participante=participante),
            'promedio': evaluaciones.filter(
                participante=participante, calificacion__isnull=False
            ).aggregate(Avg('calificacion'))['calificacion__avg']
        }
    
    # Estadísticas generales
    promedio_general = evaluaciones.filter(
        calificacion__isnull=False
    ).aggregate(Avg('calificacion'))['calificacion__avg']
    
    # Distribución de niveles de logro
    niveles_logro = evaluaciones.values('nivel_logro').annotate(
        count=Count('nivel_logro')
    ).order_by('nivel_logro')
    
    distribucion_logros = {}
    total_evaluaciones = evaluaciones.count()
    for nivel in niveles_logro:
        nivel_nombre = dict(Evaluacion.LOGRO_CHOICES).get(nivel['nivel_logro'], nivel['nivel_logro'])
        distribucion_logros[nivel_nombre] = {
            'count': nivel['count'],
            'porcentaje': (nivel['count'] / total_evaluaciones) * 100 if total_evaluaciones > 0 else 0
        }
    
    return render(request, 'talleres/reporte_evaluaciones.html', {
        'taller': taller,
        'evaluaciones_por_participante': evaluaciones_por_participante,
        'promedio_general': promedio_general,
        'distribucion_logros': distribucion_logros
    })


@permiso_talleres_required
def generar_certificado(request, participante_id):
    """
    Vista para generar un certificado para un participante.
    
    Crea un certificado en PDF para el participante del taller especificado.
    
    Args:
        request: HttpRequest
        participante_id: ID del participante
        
    Returns:
        HttpResponse: Archivo PDF con el certificado
    """
    import os
    from django.conf import settings
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    
    # Obtener el participante y su taller
    participante = get_object_or_404(Participante, pk=participante_id)
    taller = participante.taller
    
    # Solo generar certificados para participantes confirmados
    if participante.estado != 'CONFIRMADO':
        messages.error(request, 'Solo se pueden generar certificados para participantes con estado CONFIRMADO.')
        return redirect('participante_detail', pk=participante_id)
    
    # Solo generar certificados para talleres finalizados
    if taller.estado != 'FINALIZADO':
        messages.error(request, 'Solo se pueden generar certificados para talleres que han finalizado.')
        return redirect('participante_detail', pk=participante_id)
    
    # Verificar asistencia mínima (80%)
    total_sesiones = Asistencia.objects.filter(participante=participante).count()
    asistencias_presentes = Asistencia.objects.filter(
        participante=participante, 
        estado__in=['PRESENTE', 'TARDANZA']
    ).count()
    
    certificado_oficial = True
    if total_sesiones > 0:
        porcentaje_asistencia = (asistencias_presentes / total_sesiones) * 100
        if porcentaje_asistencia < 80:
            certificado_oficial = False
            messages.warning(
                request, 
                f'El participante tiene {porcentaje_asistencia:.1f}% de asistencia, ' +
                'lo cual es menor al 80% requerido para un certificado oficial. ' +
                'Se generará un certificado con marca de agua "NO OFICIAL".'
            )
    
    # Calcular duración del taller (en horas)
    # Asumimos 2 horas por sesión, 3 días a la semana durante el período del taller
    dias_totales = (taller.fecha_fin - taller.fecha_inicio).days + 1
    semanas = dias_totales / 7
    duracion = int(semanas * 3 * 2)  # 3 días por semana, 2 horas por día
    
    # Verificar si ya existe un certificado para este participante
    from .models import Certificado
    certificado_existente = Certificado.objects.filter(
        participante=participante,
        estado='EMITIDO'
    ).first()
    
    if certificado_existente:
        # Usar el código del certificado existente
        certificado_id = certificado_existente.codigo
    else:
        # Crear un nuevo registro de certificado
        certificado = Certificado.objects.create(
            participante=participante,
            observaciones='Certificado ' + ('oficial' if certificado_oficial else 'no oficial (asistencia insuficiente)')
        )
        certificado_id = certificado.codigo
    
    # Ruta al logo
    logo_url = os.path.join(settings.STATIC_URL, 'images/logo-white.png')
    logo_path = os.path.join(settings.STATIC_ROOT, 'images/logo-white.png')
    
    if not os.path.exists(logo_path):
        # Si no existe el archivo en STATIC_ROOT, usar la ruta directa
        logo_url = os.path.join(settings.BASE_DIR, 'static/images/logo-white.png')
    
    # Contexto para la plantilla
    context = {
        'participante': participante,
        'taller': taller,
        'duracion': duracion,
        'fecha_emision': timezone.now(),
        'certificado_id': certificado_id,
        'logo_url': logo_url,
        'certificado_oficial': certificado_oficial,
    }
    
    # Generar HTML del certificado
    html_string = render_to_string('talleres/certificados/certificado_base.html', context)
    
    # Configuración de fuentes
    font_config = FontConfiguration()
    
    # Crear PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf = html.write_pdf(
        stylesheets=[CSS(string='@page {size: letter landscape; margin: 0;}')],
        font_config=font_config
    )
    
    # Crear respuesta HTTP con el PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"certificado_{participante.nombre_completo().replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response


@permiso_talleres_required
def certificados_taller(request, taller_id):
    """
    Vista para mostrar la lista de participantes de un taller para generar certificados.
    
    Args:
        request: HttpRequest
        taller_id: ID del taller
        
    Returns:
        HttpResponse: Renderización de la plantilla con la lista de participantes
    """
    taller = get_object_or_404(Taller, pk=taller_id)
    participantes = Participante.objects.filter(taller=taller, estado='CONFIRMADO')
    
    # Obtener asistencia para cada participante
    participantes_con_asistencia = []
    for p in participantes:
        total_asistencias = Asistencia.objects.filter(participante=p).count()
        asistencias_presentes = Asistencia.objects.filter(
            participante=p, 
            estado__in=['PRESENTE', 'TARDANZA']
        ).count()
        
        if total_asistencias > 0:
            porcentaje_asistencia = (asistencias_presentes / total_asistencias) * 100
        else:
            porcentaje_asistencia = 0
        
        participantes_con_asistencia.append({
            'participante': p,
            'asistencias': asistencias_presentes,
            'total_sesiones': total_asistencias,
            'porcentaje_asistencia': porcentaje_asistencia,
            'cumple_requisito': porcentaje_asistencia >= 80
        })
    
    return render(request, 'talleres/certificados/certificados_taller.html', {
        'taller': taller,
        'participantes': participantes_con_asistencia
    })

@permiso_talleres_required
def buscar_beneficiarias(request):
    """
    Función API para buscar beneficiarias por nombre, apellido o DNI.
    Se utiliza para autocompletar campos en el formulario de participantes.
    
    Args:
        request: HttpRequest con el término de búsqueda
        
    Returns:
        JsonResponse: Lista de beneficiarias que coinciden con el término
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
            'email': b.correo if hasattr(b, 'correo') else None
        })
    
    return JsonResponse(data, safe=False)
