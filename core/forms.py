from django import forms
from .models import ConfiguracaoOED

class ConfiguracaoOEDForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoOED
        fields = ['min_pontos_clicaveis', 'max_pontos_clicaveis']
        widgets = {
            'min_pontos_clicaveis': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_pontos_clicaveis': forms.NumberInput(attrs={'class': 'form-control'}),
        }