import django_filters
from .models import Oed
from django.utils.html import strip_tags
from django import forms
from projetos.models import StatusOed, TipoOed, Projeto, Componente
from usuarios.models import Usuario


class OedFilter(django_filters.FilterSet):
    # Filtros de texto permanecem iguais
    retranca = django_filters.CharFilter(lookup_expr='icontains', label='Retranca')
    capitulo = django_filters.CharFilter(lookup_expr='icontains', label='Capítulo')
    titulo = django_filters.CharFilter(lookup_expr='icontains', label='Título')

    # Alterar para MultipleChoice nos campos de seleção
    status = django_filters.ModelMultipleChoiceFilter(
        queryset=StatusOed.objects.all(),
        label='Status'
    )
    tipo = django_filters.ModelMultipleChoiceFilter(
        queryset=TipoOed.objects.all(),
        label='Tipo'
    )
    projeto = django_filters.ModelMultipleChoiceFilter(
        queryset=Projeto.objects.all(),
        label='Projeto'
    )
    componente = django_filters.ModelMultipleChoiceFilter(
        queryset=Componente.objects.all(),
        label='Componente'
    )
    volume = django_filters.MultipleChoiceFilter(
        choices=[], # Começa vazio, preenchemos no __init__
        label='Volume',
        widget=forms.SelectMultiple(attrs={'class': 'form-control form-control-sm select-busca'})
    )
    criado_por = django_filters.ModelMultipleChoiceFilter(
        queryset=Usuario.objects.all(),
        label='Criado por'
    )
    atribuido_a = django_filters.ModelMultipleChoiceFilter(
        queryset=Usuario.objects.all(),
        label='Atribuído a'
    )

    class Meta:
        model = Oed
        fields = ['retranca', 'titulo', 'status', 'tipo', 'projeto', 'componente', 'volume', 'capitulo', 'criado_por', 'atribuido_a']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        volumes_existentes = Oed.objects.values_list('volume', flat=True).distinct().order_by('volume')
        self.filters['volume'].extra['choices'] = [
            (v, f"Volume {v}" if v else "Sem volume") for v in volumes_existentes if v is not None
        ]

        for name, field in self.form.fields.items():
            field.widget.attrs.update({'class': 'form-control form-control-sm'})
            
            # Adiciona a classe de busca se for um select (agora múltiplos)
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] += ' select-busca'
                
                if hasattr(field, 'queryset'):
                    field.label_from_instance = lambda obj: strip_tags(str(obj))