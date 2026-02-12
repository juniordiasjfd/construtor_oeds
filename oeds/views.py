from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Oed
from .forms import OedModelForm # Certifique-se de criar este form

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

    def form_valid(self, form):
        form.instance.criado_por = self.request.user # Define o autor automaticamente
        messages.success(self.request, "OED criado com sucesso.")
        return super().form_valid(form)

class OedUpdateView(LoginRequiredMixin, VerboseNameMixin, UpdateView):
    model = Oed
    form_class = OedModelForm
    template_name = 'oeds/form_generico.html'
    success_url = reverse_lazy('listar_oeds')

    def form_valid(self, form):
        messages.success(self.request, "OED atualizado com sucesso.")
        return super().form_valid(form)