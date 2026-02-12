from django.db import models
from django.conf import settings
from crum import get_current_user

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