from django.urls import path
from . import views

urlpatterns = [
    path('listar/', views.OedListView.as_view(), name='listar_oeds'),
    path('novo/', views.OedCreateView.as_view(), name='novo_oed'),
    path('editar/<int:pk>/', views.OedUpdateView.as_view(), name='editar_oed'),
]