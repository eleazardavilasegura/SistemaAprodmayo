from django.urls import path
from . import views

urlpatterns = [
    # Rutas para Beneficiarias
    path('', views.BeneficiariaListView.as_view(), name='beneficiaria_list'),
    path('nueva/', views.BeneficiariaCreateView.as_view(), name='beneficiaria_create'),
    path('<int:pk>/', views.BeneficiariaDetailView.as_view(), name='beneficiaria_detail'),
    path('<int:pk>/editar/', views.BeneficiariaUpdateView.as_view(), name='beneficiaria_update'),
    path('<int:pk>/eliminar/', views.BeneficiariaDeleteView.as_view(), name='beneficiaria_delete'),
    
    # Rutas para Acompañantes
    path('<int:pk>/acompanante/nuevo/', views.AcompananteCreateView.as_view(), name='acompanante_create'),
    path('acompanante/<int:pk>/editar/', views.AcompananteUpdateView.as_view(), name='acompanante_update'),
    path('acompanante/<int:pk>/eliminar/', views.AcompananteDeleteView.as_view(), name='acompanante_delete'),
    
    # Rutas para Hijos
    path('<int:pk>/hijo/nuevo/', views.HijoCreateView.as_view(), name='hijo_create'),
    path('hijo/<int:pk>/editar/', views.HijoUpdateView.as_view(), name='hijo_update'),
    path('hijo/<int:pk>/eliminar/', views.HijoDeleteView.as_view(), name='hijo_delete'),
    
    # Rutas para Seguimiento
    path('<int:pk>/seguimiento/nuevo/', views.SeguimientoCreateView.as_view(), name='seguimiento_create'),
    path('seguimiento/<int:pk>/editar/', views.SeguimientoUpdateView.as_view(), name='seguimiento_update'),
    path('seguimiento/<int:pk>/eliminar/', views.SeguimientoDeleteView.as_view(), name='seguimiento_delete'),
    
    # API para talleres
    path('api/buscar/', views.buscar_beneficiarias_api, name='buscar_beneficiarias_api'),
    path('api/detalle/<int:pk>/', views.detalle_beneficiaria_api, name='detalle_beneficiaria_api'),
]
