from django.db import models
from core.models import AuditoriaBase


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
    nome = models.CharField('Crédito', max_length=100, unique=True)
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
