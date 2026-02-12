from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Projeto, Componente, Credito
from .forms import ProjetoModelForm, ComponenteModelForm, CreditoModelForm
from django.shortcuts import redirect

class CoordenadorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Garante que apenas usuários logados e do grupo Coordenador acessem."""
    def test_func(self):
        return self.request.user.groups.filter(name='Coordenador').exists() or self.request.user.is_superuser
    def handle_no_permission(self):
        messages.error(self.request, "Você não tem permissão para acessar esta área.")
        return redirect('home')

class ComponenteCreateView(CoordenadorRequiredMixin, CreateView):
    model = Componente
    form_class = ComponenteModelForm
    template_name = 'projetos/form_generico.html'
    success_url = reverse_lazy('listar_componentes')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = self.model._meta.verbose_name
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Componente cadastrado com sucesso.')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao cadastrar componente. Verifique os dados.')
        return super().form_invalid(form)
class ComponenteListView(CoordenadorRequiredMixin, ListView):
    model = Componente
    template_name = 'projetos/lista_generica.html'
    context_object_name = 'componentes'
    ordering = ['nome']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verbose_name'] = self.model._meta.verbose_name
        context['verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context
    def get_create_url(self): return reverse_lazy('novo_componente')
    def get_update_url_name(self): return "editar_componente"
class ComponenteUpdateView(CoordenadorRequiredMixin, UpdateView):
    model = Componente
    form_class = ComponenteModelForm
    template_name = 'projetos/form_generico.html'
    success_url = reverse_lazy('listar_componentes')
    def form_valid(self, form):
        messages.success(self.request, 'Componente atualizado com sucesso.')
        return super().form_valid(form)


class ProjetoCreateView(CoordenadorRequiredMixin, CreateView):
    model = Projeto
    form_class = ProjetoModelForm
    template_name = 'projetos/form_generico.html'
    success_url = reverse_lazy('listar_projetos')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = self.model._meta.verbose_name
        return context
    def form_valid(self, form):
        messages.success(self.request, f'Projeto "{form.instance.nome}" criado.')
        return super().form_valid(form)
class ProjetoListView(CoordenadorRequiredMixin, ListView):
    model = Projeto
    template_name = 'projetos/lista_generica.html'
    context_object_name = 'projetos'
    ordering = ['nome']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verbose_name'] = self.model._meta.verbose_name
        context['verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context
    def get_create_url(self): return reverse_lazy('novo_projeto')
    def get_update_url_name(self): return "editar_projeto"
class ProjetoUpdateView(CoordenadorRequiredMixin, UpdateView):
    model = Projeto
    form_class = ProjetoModelForm
    template_name = 'projetos/form_generico.html'
    success_url = reverse_lazy('listar_projetos')
    def form_valid(self, form):
        messages.success(self.request, f'Projeto "{form.instance.nome}" atualizado.')
        return super().form_valid(form)

class CreditoCreateView(CoordenadorRequiredMixin, CreateView):
    model = Credito
    form_class = CreditoModelForm
    template_name = 'projetos/form_generico.html'
    success_url = reverse_lazy('listar_creditos')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = self.model._meta.verbose_name
        return context
    def form_valid(self, form):
        messages.success(self.request, 'Crédito registrado.')
        return super().form_valid(form)
class CreditoListView(CoordenadorRequiredMixin, ListView):
    model = Credito
    template_name = 'projetos/lista_generica.html'
    context_object_name = 'creditos'
    ordering = ['nome']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verbose_name'] = self.model._meta.verbose_name
        context['verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context
    def get_create_url(self): return reverse_lazy('novo_credito')
    def get_update_url_name(self): return "editar_credito"
class CreditoUpdateView(CoordenadorRequiredMixin, UpdateView):
    model = Credito
    form_class = CreditoModelForm
    template_name = 'projetos/form_generico.html'
    success_url = reverse_lazy('listar_creditos')
    def form_valid(self, form):
        messages.success(self.request, 'Crédito atualizado.')
        return super().form_valid(form)

