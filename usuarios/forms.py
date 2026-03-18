from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import ConfiguracoesDoUsuario

User = get_user_model()

class UsuarioModelForm(UserCreationForm):
    """
    Formulário para registro de novos usuários.
    Herda de UserCreationForm para já trazer validação de senha.
    """
    email = forms.EmailField(required=True, help_text="Obrigatório para recuperação de senha.")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class UsuarioActivateDeactivateForm(forms.ModelForm):
    """
    Formulário simplificado para o Coordenador ativar ou desativar usuários.
    """
    class Meta:
        model = User
        fields = ['is_active', 'groups']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'groups': forms.CheckboxSelectMultiple(),
        }

class ConfiguracoesForm(forms.ModelForm):
    class Meta:
        model = ConfiguracoesDoUsuario
        fields = ['registros_por_pagina', 'ordenar_por']
        widgets = {
            'registros_por_pagina': forms.NumberInput(attrs={'class': 'form-control'}),
            'ordenar_por': forms.Select(attrs={'class': 'form-select'}),
        }



