from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    # O Django já traz username, email, password, etc.
    # Adicionamos apenas o que for extra para o seu projeto:
    email = models.EmailField('E-mail', unique=True) # Torna o e-mail obrigatório e único
    
    # Campo para saber se o usuário foi aprovado pelo Coordenador
    aprovado = models.BooleanField('Aprovado pelo Coordenador', default=False)

    def __str__(self):
        return self.get_full_name() or self.username

class ConfiguracoesDoUsuario(models.Model):
    registros_por_pagina = models.PositiveIntegerField('Número de OEDs por página', default=100)
    class OrdenarPorChoices(models.TextChoices):
        # Valor a ser salvo no DB, Display Name na interface
        ATUALIZADO_EM_ZA = '-atualizado_em', 'Atualizado em (Z-A)'
        ATUALIZADO_EM_AZ = 'atualizado_em', 'Atualizado em (A-Z)'
        RETRANCA_ZA = '-retranca', 'Retranca (Z-A)'
        RETRANCA_AZ = 'retranca', 'Retranca (A-Z)'
        STATUS_DO_PROCESSO_ZA = '-status__nome', 'Status (Z-A)'
        STATUS_DO_PROCESSO_AZ = 'status__nome', 'Status (A-Z)'
    ordenar_por = models.CharField(
        verbose_name='Ordenar lista de OEDs por',
        max_length=50,
        choices=OrdenarPorChoices.choices,
        default=OrdenarPorChoices.ATUALIZADO_EM_ZA,
    )
    # receber_notificacoes_email = models.BooleanField("Receber notificações por e-mail", default=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='configuracoes')
    class Meta:
        verbose_name = 'Configuração do usuário'



