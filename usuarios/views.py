from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from braces.views import GroupRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UsuarioModelForm, UsuarioActivateDeactivateForm


# Referência ao modelo de usuário que será definido no settings
User = get_user_model()

# Suas Views seguem abaixo...
class UsuarioCreate(CreateView):
    model = User
    template_name = 'usuario_registro.html'
    form_class = UsuarioModelForm
    success_url = reverse_lazy('registrar_done')

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            # Busca o grupo ou cria se não existir para evitar erro 404
            grupo, created = Group.objects.get_or_create(name='Comum')
            self.object.groups.add(grupo)
            self.object.is_active = False 
            self.object.save()
            
            messages.success(self.request, "Cadastro realizado! Aguarde a aprovação.")
            return response

class UsuarioCreateDone(TemplateView):
    template_name = 'usuario_registro_done.html'

class UsuarioAprovarView(GroupRequiredMixin, UpdateView):
    group_required = [u"Coordenador"]
    model = User
    form_class = UsuarioActivateDeactivateForm
    template_name = 'usuario_aprovar_form.html' # Um template opcional para edição individual
    success_url = reverse_lazy('gerenciar_usuarios_todos')

    def form_valid(self, form):
        messages.success(self.request, f"Status do usuário {self.object.username} atualizado.")
        return super().form_valid(form)

class UsuarioListarTodosView(GroupRequiredMixin, TemplateView):
    group_required = [u"Coordenador"]
    template_name = 'usuario_gerenciamento_todos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filtramos para excluir Administradores E Superusuários
        # Também ordenamos por data de cadastro (mais recentes primeiro)
        base = User.objects.exclude(groups__name='Administrador') \
                           .filter(is_superuser=False) \
                           .order_by('-date_joined')
        
        # Separamos entre ativos e pendentes para o template
        context['usuarios_ativos'] = base.filter(is_active=True)
        context['usuarios_pendentes'] = base.filter(is_active=False)
        return context

class ConfiguracoesView(LoginRequiredMixin, TemplateView):
    template_name = 'core/configuracoes.html'






