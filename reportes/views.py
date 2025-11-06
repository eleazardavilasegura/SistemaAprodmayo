from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.utils import timezone
from django.views.generic import View
from django.template.loader import get_template
import datetime
import csv
import io
# import xlsxwriter
# from xhtml2pdf import pisa
from usuarios.decorators import permiso_reportes_required, permiso_finanzas_required, permiso_beneficiarias_required, permiso_talleres_required
from finanzas.models import Ingreso, Egreso, Socio, Categoria
from beneficiarias.models import Beneficiaria
from talleres.models import Taller, Asistencia, Evaluacion

@login_required
@permiso_reportes_required
def reportes_index(request):
    """
    Vista principal para la sección de reportes.
    Muestra enlaces a los diferentes tipos de reportes disponibles.
    """
    # Verificamos si se solicita una previsualización de PDF
    if request.GET.get('preview_pdf', False):
        tipo = request.GET.get('tipo', '')
        if tipo == 'beneficiarias':
            # Preparamos el contexto para el PDF de beneficiarias
            context = {
                'fecha_generacion': timezone.now(),
                'beneficiarias': Beneficiaria.objects.all().order_by('apellidos', 'nombres')[:10]  # Solo 10 para preview
            }
            return generar_pdf('reportes/beneficiarias_pdf.html', context)
        elif tipo == 'talleres':
            # Preparamos el contexto para el PDF de talleres
            talleres = Taller.objects.all().order_by('-fecha_inicio')[:5]  # Solo 5 para preview
            
            # Obtener asistencias asociadas con el primer taller a través de participantes
            asistencias = []
            if talleres.exists():
                primer_taller = talleres.first()
                # Obtenemos participantes del taller y luego sus asistencias
                asistencias = Asistencia.objects.filter(participante__taller=primer_taller)[:10]
            
            context = {
                'fecha_generacion': timezone.now(),
                'talleres': talleres,
                'asistencias': asistencias
            }
            return generar_pdf('reportes/talleres_pdf.html', context)
        elif tipo == 'finanzas':
            # Preparamos el contexto para el PDF de balance financiero
            hoy = timezone.now().date()
            primer_dia_mes = hoy.replace(day=1)
            ingresos = Ingreso.objects.filter(fecha__gte=primer_dia_mes).order_by('fecha')
            egresos = Egreso.objects.filter(fecha__gte=primer_dia_mes).order_by('fecha')
            total_ingresos = ingresos.aggregate(total=Sum('monto'))['total'] or 0
            total_egresos = egresos.aggregate(total=Sum('monto'))['total'] or 0
            context = {
                'fecha_generacion': timezone.now(),
                'fecha_inicio': primer_dia_mes,
                'fecha_fin': hoy,
                'ingresos': ingresos,
                'egresos': egresos,
                'total_ingresos': total_ingresos,
                'total_egresos': total_egresos,
                'balance': total_ingresos - total_egresos
            }
            return generar_pdf('reportes/balance_financiero_pdf.html', context)
    
    return render(request, 'reportes/index.html')

# Reportes de Finanzas
@login_required
@permiso_reportes_required
@permiso_finanzas_required
def reporte_balance_financiero(request):
    """
    Genera un reporte del balance financiero (ingresos vs egresos)
    """
    # Obtenemos la fecha actual y calculamos el primer día del mes actual y del mes anterior
    hoy = timezone.now().date()
    primer_dia_mes_actual = hoy.replace(day=1)
    ultimo_dia_mes_anterior = primer_dia_mes_actual - datetime.timedelta(days=1)
    primer_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)
    
    # Calculamos ingresos y egresos del mes actual
    ingresos_mes_actual = Ingreso.objects.filter(
        fecha__gte=primer_dia_mes_actual,
        fecha__lte=hoy
    ).aggregate(total=Sum('monto'))['total'] or 0
    
    egresos_mes_actual = Egreso.objects.filter(
        fecha__gte=primer_dia_mes_actual,
        fecha__lte=hoy
    ).aggregate(total=Sum('monto'))['total'] or 0
    
    # Calculamos ingresos y egresos del mes anterior
    ingresos_mes_anterior = Ingreso.objects.filter(
        fecha__gte=primer_dia_mes_anterior,
        fecha__lte=ultimo_dia_mes_anterior
    ).aggregate(total=Sum('monto'))['total'] or 0
    
    egresos_mes_anterior = Egreso.objects.filter(
        fecha__gte=primer_dia_mes_anterior,
        fecha__lte=ultimo_dia_mes_anterior
    ).aggregate(total=Sum('monto'))['total'] or 0
    
    # Calculamos el balance total histórico
    ingresos_total = Ingreso.objects.aggregate(total=Sum('monto'))['total'] or 0
    egresos_total = Egreso.objects.aggregate(total=Sum('monto'))['total'] or 0
    
    # Detalles por categoría en el mes actual
    categorias_ingresos = Ingreso.objects.filter(
        fecha__gte=primer_dia_mes_actual,
        fecha__lte=hoy
    ).values('categoria__nombre').annotate(total=Sum('monto'))
    
    categorias_egresos = Egreso.objects.filter(
        fecha__gte=primer_dia_mes_actual,
        fecha__lte=hoy
    ).values('categoria__nombre').annotate(total=Sum('monto'))
    
    # Datos para el reporte
    context = {
        'hoy': hoy,
        'primer_dia_mes_actual': primer_dia_mes_actual,
        'ultimo_dia_mes_anterior': ultimo_dia_mes_anterior,
        'primer_dia_mes_anterior': primer_dia_mes_anterior,
        'ingresos_mes_actual': ingresos_mes_actual,
        'egresos_mes_actual': egresos_mes_actual,
        'balance_mes_actual': ingresos_mes_actual - egresos_mes_actual,
        'ingresos_mes_anterior': ingresos_mes_anterior,
        'egresos_mes_anterior': egresos_mes_anterior,
        'balance_mes_anterior': ingresos_mes_anterior - egresos_mes_anterior,
        'ingresos_total': ingresos_total,
        'egresos_total': egresos_total,
        'balance_total': ingresos_total - egresos_total,
        'categorias_ingresos': categorias_ingresos,
        'categorias_egresos': categorias_egresos,
    }
    
    # Formato de exportación
    formato = request.GET.get('formato', 'html')
    
    if formato == 'pdf':
        # Agregamos información adicional para el PDF
        pdf_context = context.copy()
        pdf_context['fecha_generacion'] = timezone.now()
        
        # Obtenemos los ingresos y egresos para el periodo seleccionado
        fecha_inicio = request.GET.get('fecha_inicio', primer_dia_mes_actual.strftime('%Y-%m-%d'))
        fecha_fin = request.GET.get('fecha_fin', hoy.strftime('%Y-%m-%d'))
        
        try:
            fecha_inicio = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            fecha_inicio = primer_dia_mes_actual
            fecha_fin = hoy
        
        # Filtramos los ingresos y egresos
        ingresos = Ingreso.objects.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin).order_by('fecha')
        egresos = Egreso.objects.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin).order_by('fecha')
        
        # Calculamos totales
        total_ingresos = ingresos.aggregate(total=Sum('monto'))['total'] or 0
        total_egresos = egresos.aggregate(total=Sum('monto'))['total'] or 0
        balance = total_ingresos - total_egresos
        
        # Calculamos ingresos y egresos por categoría
        ingresos_por_categoria = []
        if total_ingresos > 0:
            ingresos_por_categoria = ingresos.values('categoria__nombre').annotate(
                total=Sum('monto')
            ).order_by('-total')
            
            # Añadir porcentaje
            for item in ingresos_por_categoria:
                item['porcentaje'] = (item['total'] / total_ingresos) * 100
        
        egresos_por_categoria = []
        if total_egresos > 0:
            egresos_por_categoria = egresos.values('categoria__nombre').annotate(
                total=Sum('monto')
            ).order_by('-total')
            
            # Añadir porcentaje
            for item in egresos_por_categoria:
                item['porcentaje'] = (item['total'] / total_egresos) * 100
        
        # Actualizamos el contexto con los datos filtrados
        pdf_context.update({
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'ingresos': ingresos,
            'egresos': egresos,
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'balance': balance,
            'ingresos_por_categoria': ingresos_por_categoria,
            'egresos_por_categoria': egresos_por_categoria
        })
        
        return generar_pdf('reportes/balance_financiero_pdf.html', pdf_context)
    elif formato == 'excel':
        return exportar_balance_financiero_excel(context)
    else:
        return render(request, 'reportes/finanzas/balance_financiero.html', context)

# Reportes de Beneficiarias
@login_required
@permiso_reportes_required
@permiso_beneficiarias_required
def reporte_beneficiarias(request):
    """
    Genera un reporte sobre las beneficiarias
    """
    # Obtenemos la fecha actual y calculamos el primer día del mes actual
    hoy = timezone.now().date()
    primer_dia_mes_actual = hoy.replace(day=1)
    
    # Beneficiarias registradas en el mes actual
    beneficiarias_mes_actual = Beneficiaria.objects.filter(
        fecha_ingreso__gte=primer_dia_mes_actual,
        fecha_ingreso__lte=hoy
    ).count()
    
    # Total de beneficiarias activas - Asumimos que todas están activas
    beneficiarias_activas = Beneficiaria.objects.count()
    
    # Total de beneficiarias inactivas - Asumimos que no hay inactivas
    beneficiarias_inactivas = 0
    
    # Total de beneficiarias
    total_beneficiarias = Beneficiaria.objects.count()
    
    # Beneficiarias por grupo etario
    beneficiarias_por_edad = {
        'menores_18': Beneficiaria.objects.filter(edad__lt=18).count(),
        '18_30': Beneficiaria.objects.filter(edad__gte=18, edad__lte=30).count(),
        '31_45': Beneficiaria.objects.filter(edad__gte=31, edad__lte=45).count(),
        '46_60': Beneficiaria.objects.filter(edad__gte=46, edad__lte=60).count(),
        'mayores_60': Beneficiaria.objects.filter(edad__gt=60).count(),
    }
    
    # Datos para el reporte
    context = {
        'hoy': hoy,
        'primer_dia_mes_actual': primer_dia_mes_actual,
        'beneficiarias_mes_actual': beneficiarias_mes_actual,
        'beneficiarias_activas': beneficiarias_activas,
        'beneficiarias_inactivas': beneficiarias_inactivas,
        'total_beneficiarias': total_beneficiarias,
        'beneficiarias_por_edad': beneficiarias_por_edad,
        'listado_beneficiarias': Beneficiaria.objects.all().order_by('apellidos', 'nombres')
    }
    
    # Formato de exportación
    formato = request.GET.get('formato', 'html')
    
    if formato == 'pdf':
        # Agregamos información adicional para el PDF
        pdf_context = context.copy()
        pdf_context['fecha_generacion'] = timezone.now()
        
        # Obtenemos las beneficiarias con sus diagnósticos y seguimientos
        beneficiarias = Beneficiaria.objects.all().order_by('apellidos', 'nombres')
        
        # Creamos una lista para almacenar las beneficiarias con sus datos adicionales
        beneficiarias_con_datos = []
        
        # Importamos los modelos necesarios
        from talleres.models import Evaluacion, Participante
        
        for beneficiaria in beneficiarias:
            # Primero buscamos los participantes asociados a esta beneficiaria
            participantes = Participante.objects.filter(
                beneficiaria=beneficiaria
            )
            
            # Obtenemos las evaluaciones para estos participantes
            if participantes.exists():
                diagnosticos = Evaluacion.objects.filter(
                    participante__in=participantes
                ).order_by('-fecha')
            else:
                # Si no hay participantes asociados a esta beneficiaria
                diagnosticos = []
            
            # Obtenemos los seguimientos de caso para esta beneficiaria
            seguimientos = beneficiaria.seguimientos.all().order_by('-fecha')
            
            # Añadimos la beneficiaria con sus datos adicionales
            beneficiaria_datos = {
                'beneficiaria': beneficiaria,
                'diagnosticos': diagnosticos,
                'seguimientos': seguimientos,
                'acompanantes': beneficiaria.acompanantes.all()
            }
            
            beneficiarias_con_datos.append(beneficiaria_datos)
            
        pdf_context['beneficiarias_con_datos'] = beneficiarias_con_datos
        
        return generar_pdf('reportes/beneficiarias_pdf.html', pdf_context)
    elif formato == 'excel':
        return exportar_beneficiarias_excel(context)
    else:
        return render(request, 'reportes/beneficiarias/reporte_beneficiarias.html', context)

# Reportes de Talleres
@login_required
@permiso_reportes_required
@permiso_talleres_required
def reporte_talleres(request):
    """
    Genera un reporte sobre los talleres
    """
    # Obtenemos la fecha actual
    hoy = timezone.now().date()
    
    # Talleres activos
    talleres_activos = Taller.objects.filter(estado='EN_CURSO').count()
    
    # Talleres finalizados
    talleres_finalizados = Taller.objects.filter(estado='FINALIZADO').count()
    
    # Total de talleres
    total_talleres = Taller.objects.count()
    
    # Asistencia promedio
    asistencia_promedio = Asistencia.objects.filter(
        estado='PRESENTE'
    ).count() / max(total_talleres, 1)
    
    # Datos para el reporte
    context = {
        'hoy': hoy,
        'talleres_activos': talleres_activos,
        'talleres_finalizados': talleres_finalizados,
        'total_talleres': total_talleres,
        'asistencia_promedio': asistencia_promedio,
        'listado_talleres': Taller.objects.all().order_by('-fecha_inicio')
    }
    
    # Formato de exportación
    formato = request.GET.get('formato', 'html')
    
    if formato == 'pdf':
        # Agregamos información adicional para el PDF
        pdf_context = context.copy()
        pdf_context['fecha_generacion'] = timezone.now()
        
        # Asegurarnos de tener todos los campos necesarios
        talleres = Taller.objects.all().order_by('-fecha_inicio')
        
        # Obtenemos el taller específico si se proporciona un ID
        taller_id = request.GET.get('taller_id', None)
        if taller_id:
            try:
                taller = Taller.objects.get(id=taller_id)
                pdf_context['talleres'] = [taller]
                pdf_context['asistencias'] = Asistencia.objects.filter(taller=taller)
            except Taller.DoesNotExist:
                pdf_context['talleres'] = talleres
        else:
            pdf_context['talleres'] = talleres
        
        return generar_pdf('reportes/talleres_pdf.html', pdf_context)
    elif formato == 'excel':
        return exportar_talleres_excel(context)
    else:
        return render(request, 'reportes/talleres/reporte_talleres.html', context)

# Funciones de generación de reportes
def generar_pdf(template_path, context):
    """
    Genera un archivo PDF a partir de una plantilla y un contexto
    NOTA: Temporalmente deshabilitado por falta de dependencias
    """
    from django.http import HttpResponse
    return HttpResponse("Funcionalidad de PDF temporalmente deshabilitada por falta de dependencias del sistema", content_type='text/plain')

def fetch_resources(uri, rel):
    """
    Callback para resolver URLs para recursos como imágenes en los PDFs
    """
    from django.conf import settings
    import os
    
    # Convertir URI a ruta del sistema de archivos
    if uri.startswith('static/'):
        path = os.path.join(settings.STATIC_ROOT, uri.replace('static/', ''))
    elif uri.startswith('/static/'):
        path = os.path.join(settings.STATIC_ROOT, uri.replace('/static/', ''))
    elif uri.startswith('media/'):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace('media/', ''))
    elif uri.startswith('/media/'):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace('/media/', ''))
    else:
        # Para otras URLs absolutas
        path = uri
    
    # Asegurarse de que el archivo existe
    if not os.path.isfile(path):
        # Si no existe, buscar en el directorio estático general
        path = os.path.join(settings.BASE_DIR, uri.lstrip('/'))
    
    # Devolver la ruta y el tipo de recurso
    return path

def exportar_balance_financiero_excel(context):
    """
    Exporta el reporte de balance financiero a Excel
    NOTA: Temporalmente deshabilitado por falta de dependencias
    """
    from django.http import HttpResponse
    return HttpResponse("Funcionalidad de Excel temporalmente deshabilitada por falta de dependencias del sistema", content_type='text/plain')
    worksheet = workbook.add_worksheet('Balance Financiero')
    
    # Formatos
    titulo = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter',
    })
    
    header = workbook.add_format({
        'bold': True,
        'bg_color': '#F7F7F7',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'border': 1
    })
    
    money_format = workbook.add_format({
        'border': 1,
        'num_format': 'S/ #,##0.00'
    })
    
    # Títulos
    worksheet.merge_range('A1:G1', 'REPORTE DE BALANCE FINANCIERO', titulo)
    worksheet.merge_range('A2:G2', f'Generado el {context["hoy"].strftime("%d/%m/%Y")}', titulo)
    
    # Datos del mes actual
    worksheet.write('A4', 'BALANCE DEL MES ACTUAL', header)
    worksheet.write('A5', 'Concepto', header)
    worksheet.write('B5', 'Monto', header)
    
    worksheet.write('A6', 'Total Ingresos', cell_format)
    worksheet.write('B6', context['ingresos_mes_actual'], money_format)
    
    worksheet.write('A7', 'Total Egresos', cell_format)
    worksheet.write('B7', context['egresos_mes_actual'], money_format)
    
    worksheet.write('A8', 'Balance', header)
    worksheet.write('B8', context['balance_mes_actual'], money_format)
    
    # Datos del mes anterior
    worksheet.write('D4', 'BALANCE DEL MES ANTERIOR', header)
    worksheet.write('D5', 'Concepto', header)
    worksheet.write('E5', 'Monto', header)
    
    worksheet.write('D6', 'Total Ingresos', cell_format)
    worksheet.write('E6', context['ingresos_mes_anterior'], money_format)
    
    worksheet.write('D7', 'Total Egresos', cell_format)
    worksheet.write('E7', context['egresos_mes_anterior'], money_format)
    
    worksheet.write('D8', 'Balance', header)
    worksheet.write('E8', context['balance_mes_anterior'], money_format)
    
    # Balance total
    worksheet.write('A10', 'BALANCE TOTAL HISTÓRICO', header)
    worksheet.write('A11', 'Concepto', header)
    worksheet.write('B11', 'Monto', header)
    
    worksheet.write('A12', 'Total Ingresos', cell_format)
    worksheet.write('B12', context['ingresos_total'], money_format)
    
    worksheet.write('A13', 'Total Egresos', cell_format)
    worksheet.write('B13', context['egresos_total'], money_format)
    
    worksheet.write('A14', 'Balance', header)
    worksheet.write('B14', context['balance_total'], money_format)
    
    # Categorías de ingresos
    worksheet.write('A16', 'DETALLE DE INGRESOS POR CATEGORÍA (MES ACTUAL)', header)
    worksheet.write('A17', 'Categoría', header)
    worksheet.write('B17', 'Monto', header)
    
    row = 17
    for categoria in context['categorias_ingresos']:
        row += 1
        worksheet.write(f'A{row}', categoria['categoria__nombre'], cell_format)
        worksheet.write(f'B{row}', categoria['total'], money_format)
    
    # Categorías de egresos
    row += 2
    worksheet.write(f'A{row}', 'DETALLE DE EGRESOS POR CATEGORÍA (MES ACTUAL)', header)
    row += 1
    worksheet.write(f'A{row}', 'Categoría', header)
    worksheet.write(f'B{row}', 'Monto', header)
    
    for categoria in context['categorias_egresos']:
        row += 1
        worksheet.write(f'A{row}', categoria['categoria__nombre'], cell_format)
        worksheet.write(f'B{row}', categoria['total'], money_format)
    
    # Ajustar anchos de columna
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 15)
    worksheet.set_column('D:D', 30)
    worksheet.set_column('E:E', 15)
    
    workbook.close()
    
    # Crear la respuesta HTTP
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=balance_financiero_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return response

def exportar_beneficiarias_excel(context):
    """
    Exporta el reporte de beneficiarias a Excel
    NOTA: Temporalmente deshabilitado por falta de dependencias
    """
    from django.http import HttpResponse
    return HttpResponse("Funcionalidad de Excel temporalmente deshabilitada por falta de dependencias del sistema", content_type='text/plain')
    worksheet = workbook.add_worksheet('Beneficiarias')
    worksheet_acompanantes = workbook.add_worksheet('Acompañantes')
    
    # Formatos
    titulo = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter',
    })
    
    header = workbook.add_format({
        'bold': True,
        'bg_color': '#F7F7F7',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'border': 1
    })
    
    # HOJA DE BENEFICIARIAS
    # Títulos
    worksheet.merge_range('A1:G1', 'REPORTE DE BENEFICIARIAS', titulo)
    worksheet.merge_range('A2:G2', f'Generado el {context["hoy"].strftime("%d/%m/%Y")}', titulo)
    
    # Resumen
    worksheet.write('A4', 'RESUMEN', header)
    worksheet.write('A5', 'Concepto', header)
    worksheet.write('B5', 'Cantidad', header)
    
    worksheet.write('A6', 'Beneficiarias registradas este mes', cell_format)
    worksheet.write('B6', context['beneficiarias_mes_actual'], cell_format)
    
    worksheet.write('A7', 'Beneficiarias activas', cell_format)
    worksheet.write('B7', context['beneficiarias_activas'], cell_format)
    
    worksheet.write('A8', 'Beneficiarias inactivas', cell_format)
    worksheet.write('B8', context['beneficiarias_inactivas'], cell_format)
    
    worksheet.write('A9', 'Total beneficiarias', cell_format)
    worksheet.write('B9', context['total_beneficiarias'], cell_format)
    
    # Por grupo etario
    worksheet.write('D4', 'POR GRUPO ETARIO', header)
    worksheet.write('D5', 'Rango de edad', header)
    worksheet.write('E5', 'Cantidad', header)
    
    worksheet.write('D6', 'Menores de 18 años', cell_format)
    worksheet.write('E6', context['beneficiarias_por_edad']['menores_18'], cell_format)
    
    worksheet.write('D7', 'Entre 18 y 30 años', cell_format)
    worksheet.write('E7', context['beneficiarias_por_edad']['18_30'], cell_format)
    
    worksheet.write('D8', 'Entre 31 y 45 años', cell_format)
    worksheet.write('E8', context['beneficiarias_por_edad']['31_45'], cell_format)
    
    worksheet.write('D9', 'Entre 46 y 60 años', cell_format)
    worksheet.write('E9', context['beneficiarias_por_edad']['46_60'], cell_format)
    
    worksheet.write('D10', 'Mayores de 60 años', cell_format)
    worksheet.write('E10', context['beneficiarias_por_edad']['mayores_60'], cell_format)
    
    # Listado de beneficiarias
    worksheet.write('A12', 'LISTADO DE BENEFICIARIAS', header)
    worksheet.write('A13', 'DNI', header)
    worksheet.write('B13', 'Apellidos', header)
    worksheet.write('C13', 'Nombres', header)
    worksheet.write('D13', 'Edad', header)
    worksheet.write('E13', 'Teléfono', header)
    worksheet.write('F13', 'Estado', header)
    worksheet.write('G13', 'Fecha de registro', header)
    
    row = 13
    for beneficiaria in context['listado_beneficiarias']:
        row += 1
        worksheet.write(f'A{row}', beneficiaria.documento_identidad, cell_format)
        worksheet.write(f'B{row}', beneficiaria.apellidos, cell_format)
        worksheet.write(f'C{row}', beneficiaria.nombres, cell_format)
        worksheet.write(f'D{row}', beneficiaria.edad, cell_format)
        worksheet.write(f'E{row}', beneficiaria.telefono, cell_format)
        
        # Corregir referencia a método get_estado_display
        estado_display = "Activa" if hasattr(beneficiaria, 'estado') and beneficiaria.estado == 'activa' else "Inactiva"
        worksheet.write(f'F{row}', estado_display, cell_format)
        
        # Comprobar si beneficiaria tiene fecha_registro antes de acceder
        fecha_registro = beneficiaria.fecha_ingreso.strftime('%d/%m/%Y') if hasattr(beneficiaria, 'fecha_ingreso') else ""
        worksheet.write(f'G{row}', fecha_registro, cell_format)
    
    # Ajustar anchos de columna en hoja de beneficiarias
    worksheet.set_column('A:A', 12)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 8)
    worksheet.set_column('E:E', 12)
    worksheet.set_column('F:F', 15)
    worksheet.set_column('G:G', 15)
    
    # HOJA DE ACOMPAÑANTES
    # Títulos
    worksheet_acompanantes.merge_range('A1:F1', 'REPORTE DE ACOMPAÑANTES', titulo)
    worksheet_acompanantes.merge_range('A2:F2', f'Generado el {context["hoy"].strftime("%d/%m/%Y")}', titulo)
    
    # Encabezados
    worksheet_acompanantes.write('A4', 'ID BENEFICIARIA', header)
    worksheet_acompanantes.write('B4', 'BENEFICIARIA', header)
    worksheet_acompanantes.write('C4', 'NOMBRE DEL ACOMPAÑANTE', header)
    worksheet_acompanantes.write('D4', 'PARENTESCO', header)
    worksheet_acompanantes.write('E4', 'TELÉFONO', header)
    worksheet_acompanantes.write('F4', 'DOCUMENTO', header)
    
    # Listado de acompañantes
    row_acompanantes = 4
    for beneficiaria in context['listado_beneficiarias']:
        acompanantes = beneficiaria.acompanantes.all() if hasattr(beneficiaria, 'acompanantes') else []
        
        for acompanante in acompanantes:
            row_acompanantes += 1
            worksheet_acompanantes.write(f'A{row_acompanantes}', beneficiaria.id, cell_format)
            worksheet_acompanantes.write(f'B{row_acompanantes}', f"{beneficiaria.nombres} {beneficiaria.apellidos}", cell_format)
            worksheet_acompanantes.write(f'C{row_acompanantes}', f"{acompanante.nombres} {acompanante.apellidos}", cell_format)
            
            # Usar el método get_parentesco_display correctamente (con paréntesis)
            parentesco_display = acompanante.get_parentesco_display() if hasattr(acompanante, 'get_parentesco_display') else acompanante.parentesco
            worksheet_acompanantes.write(f'D{row_acompanantes}', parentesco_display, cell_format)
            
            worksheet_acompanantes.write(f'E{row_acompanantes}', acompanante.telefono, cell_format)
            worksheet_acompanantes.write(f'F{row_acompanantes}', acompanante.documento_identidad, cell_format)
    
    # Ajustar anchos de columna en hoja de acompañantes
    worksheet_acompanantes.set_column('A:A', 10)
    worksheet_acompanantes.set_column('B:B', 25)
    worksheet_acompanantes.set_column('C:C', 25)
    worksheet_acompanantes.set_column('D:D', 15)
    worksheet_acompanantes.set_column('E:E', 15)
    worksheet_acompanantes.set_column('F:F', 15)
    
    workbook.close()
    
    # Crear la respuesta HTTP
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=beneficiarias_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return response

def exportar_talleres_excel(context):
    """
    Exporta el reporte de talleres a Excel
    NOTA: Temporalmente deshabilitado por falta de dependencias
    """
    from django.http import HttpResponse
    return HttpResponse("Funcionalidad de Excel temporalmente deshabilitada por falta de dependencias del sistema", content_type='text/plain')
    worksheet = workbook.add_worksheet('Talleres')
    
    # Formatos
    titulo = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter',
    })
    
    header = workbook.add_format({
        'bold': True,
        'bg_color': '#F7F7F7',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'border': 1
    })
    
    # Títulos
    worksheet.merge_range('A1:G1', 'REPORTE DE TALLERES', titulo)
    worksheet.merge_range('A2:G2', f'Generado el {context["hoy"].strftime("%d/%m/%Y")}', titulo)
    
    # Resumen
    worksheet.write('A4', 'RESUMEN', header)
    worksheet.write('A5', 'Concepto', header)
    worksheet.write('B5', 'Cantidad', header)
    
    worksheet.write('A6', 'Talleres activos', cell_format)
    worksheet.write('B6', context['talleres_activos'], cell_format)
    
    worksheet.write('A7', 'Talleres finalizados', cell_format)
    worksheet.write('B7', context['talleres_finalizados'], cell_format)
    
    worksheet.write('A8', 'Total talleres', cell_format)
    worksheet.write('B8', context['total_talleres'], cell_format)
    
    worksheet.write('A9', 'Asistencia promedio', cell_format)
    worksheet.write('B9', f'{context["asistencia_promedio"]:.2f}', cell_format)
    
    # Listado de talleres
    worksheet.write('A11', 'LISTADO DE TALLERES', header)
    worksheet.write('A12', 'Nombre', header)
    worksheet.write('B12', 'Facilitador', header)
    worksheet.write('C12', 'Fecha inicio', header)
    worksheet.write('D12', 'Fecha fin', header)
    worksheet.write('E12', 'Estado', header)
    worksheet.write('F12', 'Participantes', header)
    
    row = 12
    for taller in context['listado_talleres']:
        row += 1
        worksheet.write(f'A{row}', taller.nombre, cell_format)
        worksheet.write(f'B{row}', taller.facilitador, cell_format)
        worksheet.write(f'C{row}', taller.fecha_inicio.strftime('%d/%m/%Y'), cell_format)
        if taller.fecha_fin:
            worksheet.write(f'D{row}', taller.fecha_fin.strftime('%d/%m/%Y'), cell_format)
        else:
            worksheet.write(f'D{row}', 'En curso', cell_format)
        worksheet.write(f'E{row}', taller.get_estado_display(), cell_format)
        worksheet.write(f'F{row}', taller.participante_set.count(), cell_format)
    
    # Ajustar anchos de columna
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 15)
    worksheet.set_column('D:D', 15)
    worksheet.set_column('E:E', 15)
    worksheet.set_column('F:F', 12)
    
    workbook.close()
    
    # Crear la respuesta HTTP
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=talleres_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return response
