"""
Configuración de URLs para el módulo de finanzas.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard financiero
    path('', views.DashboardFinancieroView.as_view(), name='dashboard_financiero'),
    
    # Categorías
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/nueva/', views.CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_delete'),
    
    # Socios
    path('socios/', views.SocioListView.as_view(), name='socio_list'),
    path('socios/nuevo/', views.SocioCreateView.as_view(), name='socio_create'),
    path('socios/<int:pk>/', views.SocioDetailView.as_view(), name='socio_detail'),
    path('socios/<int:pk>/editar/', views.SocioUpdateView.as_view(), name='socio_update'),
    path('socios/<int:pk>/eliminar/', views.SocioDeleteView.as_view(), name='socio_delete'),
    
    # Pagos de socios
    path('socios/<int:socio_id>/pago/nuevo/', views.PagoSocioCreateView.as_view(), name='pago_socio_create'),
    path('pagos/<int:pk>/editar/', views.PagoSocioUpdateView.as_view(), name='pago_socio_update'),
    path('pagos/<int:pk>/eliminar/', views.PagoSocioDeleteView.as_view(), name='pago_socio_delete'),
    
    # Ingresos
    path('ingresos/', views.IngresoListView.as_view(), name='ingreso_list'),
    path('ingresos/nuevo/', views.IngresoCreateView.as_view(), name='ingreso_create'),
    path('ingresos/<int:pk>/editar/', views.IngresoUpdateView.as_view(), name='ingreso_update'),
    path('ingresos/<int:pk>/eliminar/', views.IngresoDeleteView.as_view(), name='ingreso_delete'),
    
    # Egresos
    path('egresos/', views.EgresoListView.as_view(), name='egreso_list'),
    path('egresos/nuevo/', views.EgresoCreateView.as_view(), name='egreso_create'),
    path('egresos/<int:pk>/editar/', views.EgresoUpdateView.as_view(), name='egreso_update'),
    path('egresos/<int:pk>/eliminar/', views.EgresoDeleteView.as_view(), name='egreso_delete'),
    
    # Informes financieros
    path('informes/', views.InformeFinancieroListView.as_view(), name='informe_list'),
    path('informes/nuevo/', views.InformeFinancieroCreateView.as_view(), name='informe_create'),
    path('informes/<int:pk>/', views.InformeFinancieroDetailView.as_view(), name='informe_detail'),
    path('informes/<int:pk>/pdf/', views.generar_informe_pdf, name='informe_pdf'),
    path('informes/<int:pk>/eliminar/', views.InformeFinancieroDeleteView.as_view(), name='informe_delete'),
]
