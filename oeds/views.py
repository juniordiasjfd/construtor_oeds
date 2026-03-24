from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Oed
from django.db import transaction
from .forms import OedModelForm, PontoClicavelFormSet, OedAudioForm
from projetos.models import TipoOed
from django.shortcuts import redirect
from django_filters.views import FilterView
from .filters import OedFilter
from django.db.models import Q
from django.urls import reverse
from construtor_oeds.settings import RELATORIO_API_CSV
from usuarios.views import EditorRequiredMixin


def get_configuracoes_usuario(user):
    from usuarios.models import ConfiguracoesDoUsuario
    config, _ = ConfiguracoesDoUsuario.objects.get_or_create(usuario=user)
    return config
# Mixin para compatibilidade com templates genéricos
class VerboseNameMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verbose_name'] = self.model._meta.verbose_name
        context['verbose_name_plural'] = self.model._meta.verbose_name_plural
        context['titulo'] = self.model._meta.verbose_name
        return context

class OedTipoSelectView(LoginRequiredMixin, TemplateView):
    template_name = "oeds/escolher_tipo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tipos"] = TipoOed.objects.all()
        return context

class OedListView(LoginRequiredMixin, VerboseNameMixin, FilterView):
    model = Oed
    queryset = Oed.objects.select_related(
            'criado_por',
            'tipo'
        ).prefetch_related(
            'atribuido_a',
            'pontos'
        ).select_related(
            'audio'
        ).filter(projeto__ativo=True)
    template_name = 'oeds/lista_oeds.html' # Template específico para listar OEDs
    context_object_name = 'oeds'
    filterset_class = OedFilter
    paginate_by = 20
    ordering = ['-id']

    def get_paginate_by(self, queryset):
        config = get_configuracoes_usuario(self.request.user)
        return getattr(config, 'registros_por_pagina', 20)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['relatorio_csv'] = RELATORIO_API_CSV

        # ---------------------------
        # Query string (paginação)
        # ---------------------------
        query_string_params = self.request.GET.copy()
        query_string_params.pop('page', None)
        context['query_string'] = query_string_params.urlencode()

        # ---------------------------
        # Filtros ativos (forma segura)
        # ---------------------------
        context["filtros_avancados_ativos"] = any(
            v for k, v in self.request.GET.items()
            if k in self.filterset.form.fields and v
        )
        
        return context
    
    def get_queryset(self):
        # 1. Pega o queryset base
        queryset = super().get_queryset()
        
        # 2. Lógica de Segurança: Restringe por grupo
        if self.request.user.groups.filter(name="Leitor").exists():
            return queryset.filter(
            Q(criado_por=self.request.user) | Q(atribuido_a=self.request.user)
        ).distinct()
        
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
                # Q(credito_da_imagem_principal__nome__icontains=query) |
                Q(credito_da_imagem_principal__icontains=query) |
                
                # pontos clicáveis
                Q(pontos__titulo_ponto__icontains=query) | 
                Q(pontos__texto_ponto__icontains=query) |
                Q(pontos__legenda_da_imagem_do_ponto__icontains=query) |
                Q(pontos__alt_text_da_imagem_do_ponto__icontains=query) |
                Q(pontos__retranca_da_imagem_do_ponto__icontains=query) |
                # Q(pontos__credito_da_imagem_do_ponto__nome__icontains=query) |
                Q(pontos__credito_da_imagem_do_ponto__icontains=query) |

                # inclusão para o tipo áudio
                Q(audio__transcricao_do_audio__icontains=query) |
                Q(audio__creditos_do_audio__icontains=query) |
                Q(audio__retranca_do_audio__icontains=query)
                
            ).distinct()
        
        # Para outros grupos (como Coordenadores), retorna a lista completa
        try:
            config = get_configuracoes_usuario(self.request.user)
            preferencia_ordem = config.ordenar_por
            queryset = queryset.order_by(preferencia_ordem)
        except:
            queryset = queryset.order_by('-atualizado_em')
        return queryset

    def get_create_url(self):
        return reverse_lazy('novo_oed')

    def get_update_url_name(self):
        return "editar_oed"

class OedCreateView(EditorRequiredMixin, VerboseNameMixin, CreateView):
    model = Oed
    form_class = OedModelForm
    template_name = 'oeds/form_oed.html'
    success_url = reverse_lazy('listar_oeds')

    def get_context_data_old(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['pontos'] = PontoClicavelFormSet(self.request.POST, self.request.FILES)
        else:
            data['pontos'] = PontoClicavelFormSet()
        return data
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        motor = self.tipo.motor_de_renderizacao
        data["tipo"] = self.tipo

        audio_form = kwargs.get("audio_form")
        pontos = kwargs.get("pontos")

        if motor == TipoOed.MotorDeRenderizacao.FAIXA_AUDIO:
            data["audio_form"] = OedAudioForm(
                self.request.POST or None,
                self.request.FILES or None
            )
            data["pontos"] = None
        else:
            data["pontos"] = PontoClicavelFormSet(
                self.request.POST or None,
                self.request.FILES or None
            )
            data["audio_form"] = None

        return data
    
    def form_valid_old(self, form):
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
            # VERIFICAÇÃO DO BOTÃO FLUTUANTE
            if "_continue" in self.request.POST:
                # Redireciona para a mesma página de edição usando o ID do objeto salvo
                # Certifique-se de que o nome da URL de edição é 'editar_oed'
                return redirect(reverse('editar_oed', kwargs={'pk': self.object.pk}))
            return super().form_valid(form)
        else:
            # Se o formset for inválido, renderiza a página novamente com os erros
            messages.error(self.request, "Erro ao salvar: verifique os campos dos Pontos Clicáveis.")
            return self.render_to_response(self.get_context_data(form=form, pontos=pontos))
    
    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        messages.error(self.request, "Erro ao salvar. Verifique os campos do formulário.")
        return self.render_to_response(context)

    def form_valid(self, form):
        context = self.get_context_data()
        pontos = context.get("pontos")
        audio_form = context.get("audio_form")

        motor = self.tipo.motor_de_renderizacao

        if motor == TipoOed.MotorDeRenderizacao.FAIXA_AUDIO:
            if audio_form and not audio_form.is_valid():
                print("ERRO AUDIO_FORM:", audio_form.errors)
                context = self.get_context_data(
                        form=form,
                        audio_form=audio_form
                    )
                return self.render_to_response(context)
        else:
            if pontos and not pontos.is_valid():
                print("ERRO PONTOS:", pontos.errors)
                context = self.get_context_data(form=form)
                return self.render_to_response(context)

        with transaction.atomic():
            form.instance.criado_por = self.request.user
            form.instance.tipo = self.tipo
            self.object = form.save()

            if motor == TipoOed.MotorDeRenderizacao.FAIXA_AUDIO:
                if audio_form:
                    audio = audio_form.save(commit=False)
                    audio.oed = self.object
                    audio.save()

            else:
                pontos.instance = self.object
                pontos.save()

        messages.success(self.request, "OED criado com sucesso.")

        if "_continue" in self.request.POST:
            return redirect(reverse('editar_oed', kwargs={'pk': self.object.pk}))

        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        self.tipo_id = request.GET.get("tipo")

        if not self.tipo_id:
            return redirect("novo_oed")

        self.tipo = TipoOed.objects.get(pk=self.tipo_id)

        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tipo"] = self.tipo
        return kwargs

class OedUpdateView(EditorRequiredMixin, VerboseNameMixin, UpdateView):
    model = Oed
    form_class = OedModelForm
    template_name = 'oeds/form_oed.html'
    success_url = reverse_lazy('listar_oeds')

    def get_context_data_old(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['pontos'] = PontoClicavelFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['pontos'] = PontoClicavelFormSet(instance=self.object)
        return data
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["tipo"] = self.object.tipo
        motor = self.object.tipo.motor_de_renderizacao

        if motor == TipoOed.MotorDeRenderizacao.FAIXA_AUDIO:
            data["audio_form"] = OedAudioForm(
                self.request.POST or None,
                self.request.FILES or None,
                instance=getattr(self.object, "audio", None)
            )
            data["pontos"] = None

        else:
            if self.request.POST:
                data["pontos"] = PontoClicavelFormSet(
                    self.request.POST,
                    self.request.FILES,
                    instance=self.object
                )
            else:
                data["pontos"] = PontoClicavelFormSet(instance=self.object)

            data["audio_form"] = None
        return data

    def form_valid_old(self, form):
        context = self.get_context_data()
        pontos = context['pontos']

        if pontos.is_valid():
            with transaction.atomic():
                self.object = form.save()
                pontos.instance = self.object
                pontos.save()

            messages.success(self.request, "OED salvo com sucesso.")
            # VERIFICAÇÃO DO BOTÃO FLUTUANTE
            if "_continue" in self.request.POST:
                # Redireciona para a mesma página de edição usando o ID do objeto salvo
                # Certifique-se de que o nome da URL de edição é 'editar_oed'
                return redirect(reverse('editar_oed', kwargs={'pk': self.object.pk}))
            return redirect(self.success_url)
        else:
            messages.error(self.request, "Erro ao salvar: verifique os campos dos Pontos Clicáveis.")
            return self.render_to_response(self.get_context_data(form=form))
    
    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        messages.error(self.request, "Erro ao salvar. Verifique os campos do formulário.")
        return self.render_to_response(context)

    def form_valid(self, form):
        context = self.get_context_data()
        pontos = context.get("pontos")
        audio_form = context.get("audio_form")

        motor = self.object.tipo.motor_de_renderizacao

        if motor == TipoOed.MotorDeRenderizacao.FAIXA_AUDIO:
            if audio_form and not audio_form.is_valid():
                return self.form_invalid(form)
        else:
            if pontos and not pontos.is_valid():
                return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save()

            if motor == TipoOed.MotorDeRenderizacao.FAIXA_AUDIO:
                audio = audio_form.save(commit=False)
                audio.oed = self.object
                audio.save()

            else:
                pontos.instance = self.object
                pontos.save()

        messages.success(self.request, "OED salvo com sucesso.")

        if "_continue" in self.request.POST:
            return redirect(reverse('editar_oed', kwargs={'pk': self.object.pk}))

        return redirect(self.success_url)
    
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.tipo = self.object.tipo
        if self.object.status.only_coordenador_can_edit:
            if not (
                request.user.groups.filter(name="Coordenador").exists() or \
                self.request.user.is_superuser
            ):
                messages.error(
                    request,
                    "Este OED só pode ser editado pelo coordenador."
                )
                request.session["show_error_modal"] = True
                return redirect("listar_oeds")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tipo"] = self.object.tipo
        return kwargs

