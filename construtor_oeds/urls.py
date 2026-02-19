"""
URL configuration for construtor_oeds project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Importa o seu settings.py
from django.conf.urls.static import static # Função para servir arquivos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('usuarios.urls')),
    path('projetos/', include('projetos.urls')),
    path('oeds/', include('oeds.urls')),
    path('oeds/preview/', include('oeds_preview.urls', namespace='oeds_preview')),

    # Rota necessária para o upload de imagens do CKEditor 5
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

# Servir arquivos de mídia e estáticos durante o desenvolvimento
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)