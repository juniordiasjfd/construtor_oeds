import django_filters
from .models import Oed
from django.utils.html import strip_tags
from django import forms
from projetos.models import StatusOed, TipoOed, Projeto, Componente
from usuarios.models import Usuario


class OedFilter(django_filters.FilterSet):
    # Filtros de texto permanecem iguais
    retranca = django_filters.CharFilter(lookup_expr='icontains', label='Retranca')
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
    criado_por = django_filters.ModelMultipleChoiceFilter(
        queryset=Usuario.objects.all(),
        label='Criado por'
    )

    class Meta:
        model = Oed
        fields = ['retranca', 'titulo', 'status', 'tipo', 'projeto', 'componente', 'criado_por']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.form.fields.items():
            field.widget.attrs.update({'class': 'form-control form-control-sm'})
            
            # Adiciona a classe de busca se for um select (agora múltiplos)
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] += ' select-busca'
                
                if hasattr(field, 'queryset'):
                    field.label_from_instance = lambda obj: strip_tags(str(obj))