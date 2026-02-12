from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from projetos.models import Projeto, Componente
from django.contrib.postgres.fields import ArrayField


class Oed(models.Model):
    TIPOS_CHOICES = [
        ('infografico', 'Infográfico'),
        ('mapa', 'Mapa clicável'),
    ]
    titulo = CKEditor5Field("Título do OED", config_name='default')
    def clean(self):
        # strip_tags remove as tags HTML para checar se existe texto real
        if not strip_tags(self.titulo).strip():
            raise ValidationError({'titulo': "O título não pode estar vazio."})
        
    slug = models.SlugField(verbose_name='Retranca', unique=True, blank=True, null=True)
    tipo = models.CharField("Tipo de OED", max_length=20, choices=TIPOS_CHOICES, default='infografico')
    
    projeto = models.ForeignKey(
        Projeto, 
        on_delete=models.SET_NULL, 
        blank=True,
        null=True,
        verbose_name="Projeto",
        related_name="%(class)s_oeds"
    )
    componente = models.ForeignKey(
        Componente, 
        on_delete=models.SET_NULL, 
        blank=True,
        null=True,
        verbose_name="Componente",
        related_name="%(class)s_oeds"
    )
    
    volume = models.PositiveIntegerField("Volume", blank=True, null=True)
    capitulo = models.CharField("Capítulo", max_length=100, blank=True, null=True)
    pagina = models.PositiveIntegerField("Página", blank=True, null=True)
    local_insercao = models.CharField("Local de inserção", max_length=255, blank=True, null=True)

    # Usamos a config 'default' que já possui a classe 'Destaque Amarelo' no seu settings.py
    introducao = CKEditor5Field("Texto de introdução", config_name='default', blank=True, null=True)
    conclusao = CKEditor5Field("Texto de conclusão", config_name='default', blank=True, null=True)
    
    palavras_chave = models.CharField("Palavras-chave", blank=True, null=True, help_text='Separe por vírgulas: palavra1, palavra2')
    
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

class PontoClicavel(models.Model):
    oed = models.ForeignKey(Oed, related_name='pontos', on_delete=models.CASCADE)
    titulo_ponto = models.CharField("Título do ponto", max_length=50)
    
    # WYSIWYG para o conteúdo do Pop Up
    texto_popup = CKEditor5Field("Texto explicativo (Pop Up)", config_name='default')
    
    # ... campos de imagem conforme o briefing ...
    possui_imagem = models.BooleanField("Haverá imagem no Pop Up?", default=False)