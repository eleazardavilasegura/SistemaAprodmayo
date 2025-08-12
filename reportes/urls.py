from django.urls import path
from . import views

urlpatterns = [
    path('', views.reportes_index, name='reportes_index'),
    path('finanzas/balance/', views.reporte_balance_financiero, name='reporte_balance_financiero'),
    path('beneficiarias/', views.reporte_beneficiarias, name='reporte_beneficiarias'),
    path('talleres/', views.reporte_talleres, name='reporte_talleres'),
]
