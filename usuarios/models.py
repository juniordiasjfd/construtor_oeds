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