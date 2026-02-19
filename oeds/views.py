from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Oed
from django.db import transaction
from .forms import OedModelForm, PontoClicavelFormSet
from django.shortcuts import redirect
from django_filters.views import FilterView
from .filters import OedFilter
from django.db.models import Q


# Mixin para compatibilidade com templates genéricos
class VerboseNameMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verbose_name'] = self.model._meta.verbose_name
        context['verbose_name_plural'] = self.model._meta.verbose_name_plural
        context['titulo'] = self.model._meta.verbose_name
        return context

class OedListView(LoginRequiredMixin, VerboseNameMixin, FilterView):
    model = Oed
    template_name = 'oeds/lista_oeds.html' # Template específico para listar OEDs
    context_object_name = 'oeds'
    filterset_class = OedFilter
    paginate_by = 20
    ordering = ['-id']

    def get_queryset(self):
        # 1. Pega o queryset base
        queryset = super().get_queryset()
        
        # 2. Lógica de Segurança: Restringe por grupo
        if self.request.user.groups.filter(name="Comum externo").exists():
            return queryset.filter(criado_por=self.request.user)
        
        # 3. Busca Global "Estilo Google" (parâmetro 'q')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                # OED
                Q(retranca__icontains=query) |
                Q(titulo__icontains=query) |
                Q(introducao__icontains=query) |
                Q(conclusao__icontains=query) |
                Q(palavras_chave__icontains=query) |
                Q(fonte_de_pesquisa__icontains=query) |
                Q(legenda_da_imagem_principal__icontains=query) |
                Q(alt_text_da_imagem_principal__icontains=query) |
                Q(orientacoes_para_producao__icontains=query) |
                Q(local_insercao__icontains=query) |
                Q(retranca_da_imagem_principal__icontains=query) |
                Q(credito_da_imagem_principal__nome__icontains=query) |
                
                # pontos clicáveis
                Q(pontos__titulo_ponto__icontains=query) | 
                Q(pontos__texto_ponto__icontains=query) |
                Q(pontos__legenda_da_imagem_do_ponto__icontains=query) |
                Q(pontos__alt_text_da_imagem_do_ponto__icontains=query) |
                Q(pontos__retranca_da_imagem_do_ponto__icontains=query) |
                Q(pontos__credito_da_imagem_do_ponto__nome__icontains=query)
                
            ).distinct()
        
        # Para outros grupos (como Coordenadores), retorna a lista completa
        return queryset

    def get_create_url(self):
        return reverse_lazy('novo_oed')

    def get_update_url_name(self):
        return "editar_oed"

class OedCreateView(LoginRequiredMixin, VerboseNameMixin, CreateView):
    model = Oed
    form_class = OedModelForm
    template_name = 'oeds/form_oed.html'
    success_url = reverse_lazy('listar_oeds')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['pontos'] = PontoClicavelFormSet(self.request.POST, self.request.FILES)
        else:
            data['pontos'] = PontoClicavelFormSet()
        return data
    
    def form_valid(self, form):
        context = self.get_context_data()
        pontos = context['pontos']
        if form.is_valid() and pontos.is_valid():
            with transaction.atomic():
                form.instance.criado_por = self.request.user #
                self.object = form.save()
                if pontos.is_valid():
                    pontos.instance = self.object
                    pontos.save()
            messages.success(self.request, "OED e pontos criados com sucesso.")
            return super().form_valid(form)
        else:
            # Se o formset for inválido, renderiza a página novamente com os erros
            messages.error(self.request, "Erro ao salvar: verifique os campos dos Pontos Clicáveis.")
            return self.render_to_response(self.get_context_data(form=form, pontos=pontos))

class OedUpdateView(LoginRequiredMixin, VerboseNameMixin, UpdateView):
    model = Oed
    form_class = OedModelForm
    template_name = 'oeds/form_oed.html'
    success_url = reverse_lazy('listar_oeds')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['pontos'] = PontoClicavelFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['pontos'] = PontoClicavelFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        pontos = context['pontos']

        if pontos.is_valid():
            with transaction.atomic():
                self.object = form.save()
                pontos.instance = self.object
                pontos.save()

            messages.success(self.request, "OED salvo com sucesso.")
            return redirect(self.success_url)
        else:
            messages.error(self.request, "Erro ao salvar: verifique os campos dos Pontos Clicáveis.")
            return self.render_to_response(self.get_context_data(form=form))