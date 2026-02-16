from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # URLs para PROJETO
    path('projeto/listar/', views.ProjetoListView.as_view(), name='listar_projetos'),
    path('projeto/novo/', views.ProjetoCreateView.as_view(), name='novo_projeto'),
    path('projeto/editar/<int:pk>/', views.ProjetoUpdateView.as_view(), name='editar_projeto'),

    # URLs para COMPONENTE
    path('componente/listar/', views.ComponenteListView.as_view(), name='listar_componentes'),
    path('componente/novo/', views.ComponenteCreateView.as_view(), name='novo_componente'),
    path('componente/editar/<int:pk>/', views.ComponenteUpdateView.as_view(), name='editar_componente'),

    # URLs para CREDITO
    path('credito/listar/', views.CreditoListView.as_view(), name='listar_creditos'),
    path('credito/novo/', views.CreditoCreateView.as_view(), name='novo_credito'),
    path('credito/editar/<int:pk>/', views.CreditoUpdateView.as_view(), name='editar_credito'),

    # URLs para STATUS de OED
    path('status-oed/listar/', views.StatusOedListView.as_view(), name='listar_status_oed'),
    path('status-oed/novo/', views.StatusOedCreateView.as_view(), name='novo_status_oed'),
    path('status-oed/editar/<int:pk>/', views.StatusOedUpdateView.as_view(), name='editar_status_oed'),

    # URLs para TIPOS de OED
    path('tipo-oed/listar/', views.TipoOedListView.as_view(), name='listar_tipo_oed'),
    path('tipo-oed/novo/', views.TipoOedCreateView.as_view(), name='novo_tipo_oed'),
    path('tipo-oed/editar/<int:pk>/', views.TipoOedUpdateView.as_view(), name='editar_tipo_oed'),
]