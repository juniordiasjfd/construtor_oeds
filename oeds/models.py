from django.db import models
from django.conf import settings
# from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from projetos.models import Projeto, Componente, StatusOed, Credito
from core.models import AuditoriaBase, ConfiguracaoOED
from django.core.validators import FileExtensionValidator
import os
import uuid


def renomear_imagem_oed(instance, filename):
    """
    Função para renomear o arquivo: gera um UUID e mantém a extensão original.
    """
    ext = filename.split('.')[-1]
    novo_nome = f"{uuid.uuid4()}.{ext}"
    return os.path.join('oeds/images/', novo_nome)
class Oed(AuditoriaBase):
    retranca = models.CharField(verbose_name='Retranca', max_length=50, unique=True, help_text='Campo obrigatório. A retranca pode ser alterada posteriormente, se necessário.')
    status = models.ForeignKey(
        StatusOed,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Status do OED',
        related_name='%(class)s_oeds'
    )
    TIPOS_CHOICES = [
        ('infografico', 'Infográfico'),
        ('mapa', 'Mapa clicável'),
    ]
    titulo = CKEditor5Field("Título do OED", config_name='default')
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
    fonte_de_pesquisa = CKEditor5Field("Fonte de pesquisa", config_name='default', blank=True, null=True)
    # imagem principal
    retranca_da_imagem_principal = models.CharField(
        verbose_name='Retranca da imagem', 
        max_length=255, 
        blank=True, 
        null=True,
        help_text='Esse campo será atualizado ao carregar a imagem e salvar o OED.'
    )
    imagem_principal = models.ImageField(
        verbose_name="Imagem principal",
        upload_to=renomear_imagem_oed, # Usa a função de renomeação
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])],
        help_text="Formatos aceitos: PNG, JPG ou JPEG. Ao carregar nova imagem, o campo 'Retranca da imagem' será atualizado.",
        blank=True, 
        null=True,
    )
    legenda_da_imagem_principal = CKEditor5Field("Legenda da imagem principal", config_name='default', blank=True, null=True)
    alt_text_da_imagem_principal = models.TextField('Descrição para acessibilidade da imagem principal', max_length=2000, help_text='Máximo 2.000 caracteres.', blank=True, null=True)
    # credito_da_imagem_principal = CKEditor5Field("Crédito da imagem principal", config_name='default', blank=True, null=True)
    credito_da_imagem_principal = models.ForeignKey(
        Credito,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Crédito da imagem principal',
        related_name='%(class)s_oeds'
    )
    quantidade_pontos_prevista = models.PositiveIntegerField(
        "Quantidade de pontos clicáveis", 
        default=1,
        help_text="Informe quantos pontos clicáveis este OED deve ter."
    )
    orientacoes_para_producao = CKEditor5Field("Orientações para a produção", config_name='default', blank=True, null=True)
    @property
    def total_pontos_cadastrados(self):
        if not self.pk:
            return 0
        return self.pontos.count()
    def clean(self):
        # Chama a validação do título que já existia
        if not strip_tags(self.titulo).strip():
            raise ValidationError({'titulo': "O título não pode estar vazio."})

        # Busca a configuração ativa (assumindo que existe apenas uma)
        config = ConfiguracaoOED.objects.first()
        if config:
            if self.quantidade_pontos_prevista < config.min_pontos_clicaveis or \
               self.quantidade_pontos_prevista > config.max_pontos_clicaveis:
                raise ValidationError({
                    'quantidade_pontos_prevista': 
                    f"A quantidade de pontos deve estar entre {config.min_pontos_clicaveis} e {config.max_pontos_clicaveis}."
                })
        super().clean()
    def save(self, *args, **kwargs):
        # Verifica se há uma nova imagem sendo enviada
        if self.imagem_principal and not self.pk:
            # Captura o nome original (basename) sem a extensão
            nome_original = os.path.splitext(self.imagem_principal.name)[0]
            self.retranca_da_imagem_principal = nome_original
        # Caso queira atualizar a retranca mesmo se já existir o objeto (opcional)
        elif self.imagem_principal and self.pk:
            old_instance = Oed.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.imagem_principal != self.imagem_principal:
                 nome_original = os.path.splitext(self.imagem_principal.name)[0]
                 self.retranca_da_imagem_principal = nome_original
        super().save(*args, **kwargs)

class PontoClicavel(AuditoriaBase):
    oed = models.ForeignKey(Oed, related_name='pontos', on_delete=models.CASCADE)
    titulo_ponto = CKEditor5Field("Título do ponto", config_name='default')
    coordenadas = models.CharField(
        "Coordenadas (X,Y)", 
        max_length=50, 
        null=True, 
        blank=True,
        help_text="Clique na imagem acima para definir a posição."
    )
    texto_ponto = CKEditor5Field("Texto do ponto", config_name='default', blank=True, null=True)
    # possui_imagem = models.BooleanField("Haverá imagem no ponto?", default=True)
    retranca_da_imagem_do_ponto = models.CharField(
        verbose_name='Retranca da imagem', 
        max_length=255, 
        blank=True, 
        null=True,
        help_text='Esse campo será atualizado ao carregar a imagem e salvar.'
    )
    imagem_do_ponto = models.ImageField(
        verbose_name="Imagem do ponto",
        upload_to=renomear_imagem_oed, # Usa a função de renomeação
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])],
        help_text="Formatos aceitos: PNG, JPG ou JPEG. Ao carregar nova imagem, o campo 'Retranca da imagem' será atualizado.",
        blank=True, 
        null=True,
    )
    legenda_da_imagem_do_ponto = CKEditor5Field("Legenda da imagem", config_name='default', blank=True, null=True)
    alt_text_da_imagem_do_ponto = models.TextField('Descrição para acessibilidade', max_length=2000, help_text='Máximo 2.000 caracteres.', blank=True, null=True)
    # credito_da_imagem_do_ponto = CKEditor5Field("Crédito da imagem", config_name='default', blank=True, null=True)
    credito_da_imagem_do_ponto = models.ForeignKey(
        Credito,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Crédito da imagem',
        related_name='%(class)s_oeds'
    )
    def clean(self):
        # strip_tags remove as tags HTML para checar se existe texto real
        if not self.titulo_ponto or not strip_tags(self.titulo_ponto).strip():
            raise ValidationError({'titulo_ponto': "O título não pode estar vazio."})
        if not self.pk: # Apenas para novos registros
            if self.oed.total_pontos_cadastrados >= self.oed.quantidade_pontos_prevista:
                raise ValidationError(
                    f"Este OED já atingiu o limite de {self.oed.quantidade_pontos_prevista} pontos previstos."
                )
        super().clean()
    def save(self, *args, **kwargs):
        # Verifica se há uma nova imagem sendo enviada
        if self.imagem_do_ponto and not self.pk:
            # Captura o nome original (basename) sem a extensão
            nome_original = os.path.splitext(self.imagem_do_ponto.name)[0]
            self.retranca_da_imagem_do_ponto = nome_original
        # Caso queira atualizar a retranca mesmo se já existir o objeto (opcional)
        elif self.imagem_do_ponto and self.pk:
            old_instance = PontoClicavel.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.imagem_do_ponto != self.imagem_do_ponto:
                 nome_original = os.path.splitext(self.imagem_do_ponto.name)[0]
                 self.retranca_da_imagem_do_ponto = nome_original
        super().save(*args, **kwargs)