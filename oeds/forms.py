from django import forms
from django.forms import inlineformset_factory
from .models import Oed, PontoClicavel
from django_ckeditor_5.widgets import CKEditor5Widget
from django.utils.html import strip_tags


class OedModelForm(forms.ModelForm):
    # Declaramos como campos extras para contornar o erro de "non-editable field"
    criado_em = forms.CharField(label="Criado em", required=False)
    atualizado_em = forms.CharField(label="Atualizado em", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # 1. Primeiro verificamos se é um Checkbox
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            # 2. Se for CKEditor, não adicionamos classes extras (ele já tem as dele)
            elif isinstance(field.widget, CKEditor5Widget):
                continue
            # 3. Para todos os outros campos (Texto, Select, etc), usamos form-control
            else:
                field.widget.attrs.update({'class': 'form-control'})

        # Preenche os campos informativos se o objeto já existir
        if self.instance and self.instance.pk:
            if self.instance.criado_em:
                self.initial['criado_em'] = self.instance.criado_em.strftime('%d/%m/%Y %H:%M')
            if self.instance.atualizado_em:
                self.initial['atualizado_em'] = self.instance.atualizado_em.strftime('%d/%m/%Y %H:%M')

        # Lista de campos que não devem ser editáveis pelo usuário
        readonly_fields = ['criado_por', 'atualizado_por', 'criado_em', 'atualizado_em']
        
        for name, field in self.fields.items():
            # Aplica Bootstrap
            if not isinstance(field.widget, CKEditor5Widget):
                field.widget.attrs.update({'class': 'form-control'})
            
            # Bloqueia os campos de autoria
            if name in readonly_fields:
                field.disabled = True
        
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                # Adiciona a classe que o JS procura
                field.widget.attrs.update({'class': 'form-select select-busca'})
                # Limpa o HTML das opções
                field.label_from_instance = lambda obj: strip_tags(str(obj))

    class Meta:
        model = Oed
        # IMPORTANTE: Remova 'criado_em' e 'atualizado_em' desta lista Meta
        fields = [
            'retranca', 'status', 'titulo', 'tipo', 'projeto', 'componente', 
            'volume', 'capitulo', 'pagina', 'local_insercao', 
            'introducao', 'retranca_da_imagem_principal', 'imagem_principal',
            'legenda_da_imagem_principal', 'alt_text_da_imagem_principal',
            'credito_da_imagem_principal',
            'conclusao', 'palavras_chave',
            'fonte_de_pesquisa', 
            'quantidade_pontos_prevista',
            'orientacoes_para_producao',
            'criado_por', 'atualizado_por'
        ]
        
        widgets = {
            "titulo": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="default"),
            "introducao": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="default"),
            "conclusao": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="default"),
            "palavras_chave": forms.TextInput(attrs={'placeholder': 'Palavras separadas por vírgula',}),
            'status': forms.Select(attrs={'class': 'form-select select-busca'}),
            'tipo': forms.Select(attrs={'class': 'form-select select-busca'}),
            'projeto': forms.Select(attrs={'class': 'form-select select-busca'}),
            'componente': forms.Select(attrs={'class': 'form-select select-busca'}),
            'credito_da_imagem_principal': forms.Select(attrs={'class': 'form-select select-busca'}),
        }

class CoordenadasWidget(forms.TextInput):
    template_name = 'oeds/coordenadas_picker.html'

class PontoClicavelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔹 Define a URL da imagem principal do OED (se existir)
        oed = getattr(self.instance, 'oed', None)

        if oed and oed.imagem_principal:
            self.fields['coordenadas'].widget.attrs.update({
                'data-img-url': oed.imagem_principal.url,
                'placeholder': 'Clique na imagem para marcar'
            })

        # 🔹 Aplica classes Bootstrap
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, CKEditor5Widget):
                continue
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                # Adiciona a classe que o JS procura
                field.widget.attrs.update({'class': 'form-select select-busca'})
                # Limpa o HTML das opções
                field.label_from_instance = lambda obj: strip_tags(str(obj))

    class Meta:
        model = PontoClicavel
        fields = [
            'titulo_ponto', 'coordenadas', 'texto_ponto', #'possui_imagem', 
            'retranca_da_imagem_do_ponto',
            'imagem_do_ponto', 'legenda_da_imagem_do_ponto', 
            'alt_text_da_imagem_do_ponto', 'credito_da_imagem_do_ponto'
        ]
        widgets = {
            "titulo_ponto": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="default"),
            "texto_ponto": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="default"),
            "legenda_da_imagem_do_ponto": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="default"),
            # "credito_da_imagem_do_ponto": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="default"),
            'coordenadas': CoordenadasWidget(),
            'credito_da_imagem_do_ponto': forms.Select(attrs={'class': 'form-select select-busca'}),
        }

# O FormSet que liga o OED aos seus pontos
PontoClicavelFormSet = inlineformset_factory(
    Oed, 
    PontoClicavel, 
    form=PontoClicavelForm,
    extra=0, # Deixamos 0 porque o JavaScript criará os campos necessários
    can_delete=True,
    max_num=10, # Defina um limite razoável para segurança
    validate_max=True
)





