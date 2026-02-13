from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Oed
from django.db import transaction
from .forms import OedModelForm, PontoClicavelFormSet

# Mixin para compatibilidade com templates genéricos
class VerboseNameMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verbose_name'] = self.model._meta.verbose_name
        context['verbose_name_plural'] = self.model._meta.verbose_name_plural
        context['titulo'] = self.model._meta.verbose_name
        return context

class OedListView(LoginRequiredMixin, VerboseNameMixin, ListView):
    model = Oed
    template_name = 'oeds/lista_oeds.html' # Template específico para listar OEDs
    context_object_name = 'oeds'
    ordering = ['-id']

    def get_create_url(self):
        return reverse_lazy('novo_oed')

    def get_update_url_name(self):
        return "editar_oed"

class OedCreateView(LoginRequiredMixin, VerboseNameMixin, CreateView):
    model = Oed
    form_class = OedModelForm
    template_name = 'oeds/form_generico.html'
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
    template_name = 'oeds/form_generico.html'
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
        if form.is_valid() and pontos.is_valid():
            with transaction.atomic():
                self.object = form.save()
                if pontos.is_valid():
                    pontos.instance = self.object
                    pontos.save()
            messages.success(self.request, "OED e pontos atualizados com sucesso.")
            return super().form_valid(form)
        else:
            # Se o formset for inválido, renderiza a página novamente com os erros
            messages.error(self.request, "Erro ao salvar: verifique os campos dos Pontos Clicáveis.")
            return self.render_to_response(self.get_context_data(form=form, pontos=pontos))