from django import forms
from .models import Oed
from django_ckeditor_5.widgets import CKEditor5Widget

class OedModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classes Bootstrap para manter o estilo do seu form_generico.html
        for field in self.fields.values():
            if not isinstance(field.widget, CKEditor5Widget):
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Oed
        # Excluímos 'criado_por' e 'slug' pois são preenchidos automaticamente na View/Model
        exclude = ['criado_por', 'slug']
        
        widgets = {
            "titulo": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="default"),
            "introducao": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="default"),
            "conclusao": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="default"),
            "palavras_chave": forms.TextInput(attrs={
                'placeholder': 'Digite as palavras separadas por vírgula e pressione Enter',
                'class': 'form-control'
            }),
        }