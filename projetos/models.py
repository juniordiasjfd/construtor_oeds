from django.db import models
from core.models import AuditoriaBase
from django_ckeditor_5.fields import CKEditor5Field



class Componente(AuditoriaBase):
    nome = models.CharField('Componente', max_length=100, unique=True)
    class Meta:
        verbose_name = 'Componente'
        verbose_name_plural = 'Componentes'
        ordering = ['nome']
    def __str__(self):
        return self.nome

class Projeto(AuditoriaBase):
    nome = models.CharField('Projeto', max_length=100, unique=True)
    editora = models.CharField('Editora', max_length=100)
    ciclo = models.CharField('Ciclo', max_length=100)
    class Meta:
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'
        ordering = ['nome']
    def __str__(self):
        return self.nome

class Credito(AuditoriaBase):
    # nome = models.CharField('Crédito', max_length=100, unique=True)
    nome = CKEditor5Field("Crédito", config_name='default')
    class Meta:
        verbose_name = 'Crédito'
        verbose_name_plural = 'Créditos'
        ordering = ['nome']
    def __str__(self):
        return self.nome

class StatusOed(AuditoriaBase):
    nome = models.CharField('Status do OED', max_length=100, unique=True)
    class Meta:
        verbose_name = 'Status do OED'
        verbose_name_plural = 'Status dos OEDs'
        ordering = ['nome']
    def __str__(self):
        return self.nome

class TipoOed(AuditoriaBase):
    class MotorDeRenderizacao(models.TextChoices):
        PONTO_CLICAVEL = "PONTO_CLICAVEL", "Ponto clicável"
        MAPA_CLICAVEL = "MAPA_CLICAVEL", "Mapa clicável"
        FAIXA_AUDIO = "FAIXA_AUDIO", "Faixa de áudio"
    nome = CKEditor5Field("Tipo", config_name='default')
    motor_de_renderizacao = models.CharField(
        "Engine",
        max_length=20,
        choices=MotorDeRenderizacao.choices,
        default=MotorDeRenderizacao.PONTO_CLICAVEL
    )
    instrucao = CKEditor5Field("Instruções", config_name='default')
    botao_fechar = models.CharField('Botão fechar', max_length=100, help_text='Necessário somente para as engines com pop-ups (modais).', default='Fechar', blank=True, null=True)
    credito_imagem_prefixo = CKEditor5Field("Prefixo do crédito da imagem", config_name='default', help_text='Necessário somente para as engines com imagens.', default='Crédito da imagem:', blank=True, null=True)
    class Meta:
        verbose_name = 'Tipo do OED'
        verbose_name_plural = 'Tipos de OED'
        ordering = ['nome']
    def __str__(self):
        return self.nome
