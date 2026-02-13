from django.contrib import admin
from .models import Oed, PontoClicavel

class PontoClicavelInline(admin.StackedInline): # Stacked ocupa melhor o espaço para campos longos
    model = PontoClicavel
    extra = 0 # Evita linhas vazias desnecessárias se o limite já foi atingido
    fields = [
        'titulo_ponto', 'texto_ponto', 'possui_imagem', 
        ('imagem_do_ponto', 'retranca_da_imagem_do_ponto'), # Exibe lado a lado
        'legenda_da_imagem_do_ponto', 'alt_text_da_imagem_do_ponto'
    ]
    readonly_fields = ['retranca_da_imagem_do_ponto'] # Campo automático

@admin.register(Oed)
class OedAdmin(admin.ModelAdmin):
    # Organiza a interface em seções lógicas
    fieldsets = (
        ('Identificação e Metadados', {
            'fields': ('retranca', 'titulo', 'tipo', ('projeto', 'componente'), ('volume', 'capitulo', 'pagina'), 'local_insercao')
        }),
        ('Conteúdo Principal', {
            'fields': ('introducao', 'conclusao', 'palavras_chave', 'orientacoes_para_producao', 'fonte_de_pesquisa')
        }),
        ('Imagem Principal', {
            'fields': (('imagem_principal', 'retranca_da_imagem_principal'), 'legenda_da_imagem_principal', 'alt_text_da_imagem_principal')
        }),
        ('Configuração de Pontos', {
            'fields': ('quantidade_pontos_prevista',)
        }),
        ('Informações de Auditoria', {
            'classes': ('collapse',), # Recolhido por padrão
            'fields': (('criado_por', 'criado_em'), ('atualizado_por', 'atualizado_em'))
        }),
    )

    inlines = [PontoClicavelInline]
    
    # Colunas visíveis na listagem principal
    list_display = ['retranca', 'tipo', 'projeto', 'quantidade_pontos_prevista', 'total_pontos_cadastrados']
    list_filter = ['tipo', 'projeto', 'componente']
    search_fields = ['retranca', 'palavras_chave']
    
    # Garante que campos automáticos não sejam editados manualmente no admin
    readonly_fields = ['retranca_da_imagem_principal', 'criado_por', 'criado_em', 'atualizado_por', 'atualizado_em']

    def save_model(self, request, obj, form, change):
        """
        Garante que o autor seja registrado corretamente pelo Admin, 
        caso a lógica de AuditoriaBase precise de suporte extra.
        """
        if not change:
            obj.criado_por = request.user
        obj.atualizado_por = request.user
        super().save_model(request, obj, form, change)