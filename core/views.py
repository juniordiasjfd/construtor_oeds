from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from usuarios.views import CoordenadorRequiredMixin
from django.views import View
from .models import ConfiguracaoOED
from .forms import ConfiguracaoOEDForm


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_projeto'] = 'Em desenvolvimento'
        return context

class ConfiguracaoOEDUpdateView(CoordenadorRequiredMixin, View):
    template_name = 'core/configuracao_oed_form.html'

    def get(self, request):
        # Busca a configuração existente ou cria uma nova instância na memória
        config, created = ConfiguracaoOED.objects.get_or_create(pk=1)
        form = ConfiguracaoOEDForm(instance=config)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        config = ConfiguracaoOED.objects.get(pk=1)
        form = ConfiguracaoOEDForm(request.POST, instance=config)
        
        if form.is_valid():
            # Validação lógica: min não pode ser maior que max
            if form.cleaned_data['min_pontos_clicaveis'] > form.cleaned_data['max_pontos_clicaveis']:
                messages.error(request, "O valor mínimo não pode ser maior que o máximo.")
            else:
                form.save()
                messages.success(request, "Configurações de OED atualizadas com sucesso!")
                return redirect('configuracoes') # Nome da sua URL de configurações
        
        return render(request, self.template_name, {'form': form})