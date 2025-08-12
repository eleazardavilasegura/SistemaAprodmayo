from django.urls import path
from . import views

urlpatterns = [
    # URLs para gestión de talleres
    path('', views.TallerListView.as_view(), name='taller_list'),
    path('nuevo/', views.TallerCreateView.as_view(), name='taller_create'),
    path('<int:pk>/', views.TallerDetailView.as_view(), name='taller_detail'),
    path('<int:pk>/editar/', views.TallerUpdateView.as_view(), name='taller_update'),
    path('<int:pk>/eliminar/', views.TallerDeleteView.as_view(), name='taller_delete'),
    
    # URLs para gestión de participantes
    path('<int:taller_id>/participantes/', views.ParticipanteListView.as_view(), name='participante_list'),
    path('<int:taller_id>/participantes/nuevo/', views.ParticipanteCreateView.as_view(), name='participante_create'),
    path('participantes/<int:pk>/', views.ParticipanteDetailView.as_view(), name='participante_detail'),
    path('participantes/<int:pk>/editar/', views.ParticipanteUpdateView.as_view(), name='participante_update'),
    path('participantes/<int:pk>/eliminar/', views.ParticipanteDeleteView.as_view(), name='participante_delete'),
    
    # URLs para gestión de asistencia
    path('<int:taller_id>/asistencia/', views.AsistenciaListView.as_view(), name='asistencia_list'),
    path('<int:taller_id>/asistencia/masiva/', views.asistencia_masiva, name='asistencia_masiva'),
    path('<int:taller_id>/asistencia/nuevo/', views.AsistenciaCreateView.as_view(), name='asistencia_create'),
    path('asistencia/<int:pk>/editar/', views.AsistenciaUpdateView.as_view(), name='asistencia_update'),
    path('asistencia/<int:pk>/eliminar/', views.AsistenciaDeleteView.as_view(), name='asistencia_delete'),
    
    # URLs para gestión de evaluaciones
    path('<int:taller_id>/evaluaciones/', views.EvaluacionListView.as_view(), name='evaluacion_list'),
    path('<int:taller_id>/evaluaciones/nuevo/', views.EvaluacionCreateView.as_view(), name='evaluacion_create'),
    path('evaluaciones/<int:pk>/', views.EvaluacionDetailView.as_view(), name='evaluacion_detail'),
    path('evaluaciones/<int:pk>/editar/', views.EvaluacionUpdateView.as_view(), name='evaluacion_update'),
    path('evaluaciones/<int:pk>/eliminar/', views.EvaluacionDeleteView.as_view(), name='evaluacion_delete'),
    
    # URLs para gestión de materiales
    path('<int:taller_id>/materiales/', views.MaterialListView.as_view(), name='material_list'),
    path('<int:taller_id>/materiales/nuevo/', views.MaterialCreateView.as_view(), name='material_create'),
    path('materiales/<int:pk>/', views.MaterialDetailView.as_view(), name='material_detail'),
    path('materiales/<int:pk>/editar/', views.MaterialUpdateView.as_view(), name='material_update'),
    path('materiales/<int:pk>/eliminar/', views.MaterialDeleteView.as_view(), name='material_delete'),
    
    # URLs para funciones AJAX
    path('buscar-beneficiarias/', views.buscar_beneficiarias, name='buscar_beneficiarias'),
    
    # URLs para reportes
    path('<int:taller_id>/reporte/asistencia/', views.reporte_asistencia, name='reporte_asistencia'),
    path('<int:taller_id>/reporte/evaluaciones/', views.reporte_evaluaciones, name='reporte_evaluaciones'),
    
    # URLs para certificados
    path('<int:taller_id>/certificados/', views.certificados_taller, name='certificados_taller'),
    path('participantes/<int:participante_id>/certificado/', views.generar_certificado, name='generar_certificado'),
]
