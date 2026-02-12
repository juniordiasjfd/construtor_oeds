from django import forms
from .models import Projeto, Componente, Credito


class ProjetoModelForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ['nome', 'editora', 'ciclo']

class CreditoModelForm(forms.ModelForm):
    class Meta:
        model = Credito
        fields = ['nome']

class ComponenteModelForm(forms.ModelForm):
    class Meta:
        model = Componente
        fields = ['nome']
