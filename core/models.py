from django.db import models
from django.conf import settings
from crum import get_current_user
from django.core.exceptions import ValidationError


class AuditoriaBase(models.Model):
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    ativo = models.BooleanField('Ativo', default=True)

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Criado por',
        related_name="%(app_label)s_%(class)s_criados"
    )
    
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Atualizado por',
        related_name="%(app_label)s_%(class)s_atualizados"
    )

    def save(self, *args, **kwargs):
        user = get_current_user()
        # Verifica se há um usuário e se ele não é anônimo
        if user and not user.is_anonymous:
            if not self.pk:
                self.criado_por = user
            self.atualizado_por = user
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class ConfiguracaoOED(models.Model):
    max_pontos_clicaveis = models.PositiveIntegerField(
        "Máximo de pontos clicáveis", 
        default=5,
        help_text="Define o máximo de pontos para cadastro de um OED."
    )
    min_pontos_clicaveis = models.PositiveIntegerField(
        "Mínimo de pontos clicáveis", 
        default=1,
        help_text="Define o mínimo de pontos para cadastro de um OED."
    )
    class Meta:
        verbose_name = "Configuração de OED"
        verbose_name_plural = "Configurações de OED"
    def save(self, *args, **kwargs):
        # Impede a criação de mais de um registro de configuração
        if not self.pk and ConfiguracaoOED.objects.exists():
            raise ValidationError("Já existe uma configuração cadastrada. Edite a existente.")
        return super().save(*args, **kwargs)
    def __str__(self):
        return "Configuração Global de OED"