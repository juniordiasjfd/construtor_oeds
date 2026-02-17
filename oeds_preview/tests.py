import os
import django
import bs4
from PIL import Image

# 1. Configura o ambiente do Django para o Shell
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construtor_oeds.settings')
django.setup()

from oeds.models import Oed
from oeds_preview.views import OedPreviewDetailView
from django.test import RequestFactory
from projetos.models import TipoOed

# 2. Simulação de um OED existente no seu banco
try:
    oed_exemplo = Oed.objects.first()
    if not oed_exemplo:
        print("Nenhum OED encontrado no banco para testar.")
    else:
        # 3. Simula a requisição e a View
        factory = RequestFactory()
        request = factory.get(f'/preview/{oed_exemplo.pk}/')
        view = OedPreviewDetailView()
        view.setup(request, pk=oed_exemplo.pk)
        view.object = oed_exemplo
        
        # 4. Executa a lógica que você quer testar
        context = view.get_context_data()
        # TIPO + TITULO
        soup_tipo = bs4.BeautifulSoup(str(context['object'].tipo), 'html.parser').p
        soup_tipo.name = 'span'
        soup_tipo['class'] = ['unwrap']
        soup_titulo = bs4.BeautifulSoup('<div class="d3tit1oed"><span class="d3titdestaque">' + str(soup_tipo) + ':</span>' + str(context['object'].titulo + '</div>'), 'html.parser')
        soup_titulo.find(attrs={'class':'unwrap'}).unwrap()
        nivel_h = 1
        for p in soup_titulo.find_all('p'):
            p.name = f'h{nivel_h}'
            nivel_h = (nivel_h + 1 if nivel_h <= 6 else nivel_h)
        soup_titulo: bs4.BeautifulSoup # capturar isso
        # INSTRUCAO + PREFIXO CRÉDITO
        tipo_oed = TipoOed.objects.filter(pk=context['object'].tipo.pk).first()
        soup_instrucao = bs4.BeautifulSoup(f'<div class="d3instrucaooed">{str(tipo_oed.instrucao)}</div>', 'html.parser')
        credito_imagem_prefixo = bs4.BeautifulSoup(tipo_oed.credito_imagem_prefixo, 'html.parser').p
        credito_imagem_prefixo.name = 'span'
        tipo_oed.botao_fechar
        soup_instrucao: bs4.BeautifulSoup # capturar isso
        # INTRODUCAO
        introducao = str(context['object'].introducao)
        introducao = bs4.BeautifulSoup(introducao, 'html.parser')
        if introducao.get_text('').strip():
            introducao = f'<div class="d3txinstrucaooed">{introducao}</div>'
        else:
            introducao = ''
        introducao: str # capturar isso
        # IMAGEM PRINCIPAL
        src_absolute = context['object'].imagem_principal.path
        src_url = context['object'].imagem_principal.url
        img = Image.open(src_absolute)
        new_width = 716
        new_height = round(img.height * (new_width/img.width))
        alt_text_da_imagem_principal = context['object'].alt_text_da_imagem_principal
        soup_imagem_principal = bs4.BeautifulSoup(f'<img alt="{alt_text_da_imagem_principal}" height="{new_height}" src="{src_url}" width="{new_width}"/>', 'html.parser')
        soup_imagem_principal: bs4.BeautifulSoup # capturar isso
        # LEGENDA
        legenda_da_imagem_principal = context['object'].legenda_da_imagem_principal
        soup_legenda_principal = bs4.BeautifulSoup(f'<div class="p4legenda">{legenda_da_imagem_principal}</div>', 'html.parser')
        soup_legenda_principal: bs4.BeautifulSoup # capturar isso
        # PONTOS
        ponto_numero = 1
        pontos_textos = []
        marcador_css = {}
        for ponto in context['pontos']:
            marcador_css[f'marcador{ponto_numero}'] = ponto.coordenadas.split(',')
            # título
            soup_ponto_titulo = bs4.BeautifulSoup(str(ponto.titulo_ponto), 'html.parser')
            soup_ponto_titulo.p.insert(0, f'{ponto_numero}. ')
            # img
            img_ponto = Image.open(ponto.imagem_do_ponto.path)
            new_width_ponto = 678
            new_height_ponto = round(img_ponto.height * (new_width_ponto/img_ponto.width))
            # construção de cada ponto
            pontos_textos += [
            f'''
            <div class="mapa-item mapa-item{ponto_numero}">
                <a class="marcador marcador{ponto_numero}" href="#marcador{ponto_numero}" id="ponto{ponto_numero}">{ponto_numero}</a>
                <div class="mapa-popup" id="marcador{ponto_numero}" role="group" aria-label="caixa de texto explicativo">
                    <div class="popup-titulo">{soup_ponto_titulo}</div>
                    <div class="col2c">
                        <figure>
                            <img alt="{ponto.alt_text_da_imagem_do_ponto}" height="{new_height_ponto}" src="{ponto.imagem_do_ponto.url}" width="{new_width_ponto}" />
                            <figcaption class="p4legenda">
                                {ponto.legenda_da_imagem_do_ponto}
                            </figcaption>
                        </figure>
                    </div>
                    <div class="d3creditoimagemoed"><span>{credito_imagem_prefixo}</span> {str(ponto.credito_da_imagem_do_ponto)}</div>
                    <div class="d3txtoedmapitem">
                         {str(ponto.texto_ponto)}
                    </div>
                    <a href="#ponto{ponto_numero}" class="btn" role="button" aria-label="fechar caixa de texto explicativo">{tipo_oed.botao_fechar}</a>
                </div>
            </div>
            '''
            ]
            ponto_numero += 1
        pontos_textos: list # capturar isso
        # FONTE DE PESQUISA E CRÉDITOS DA IMAGEM PRINCIPAL
        credito_da_imagem_principal = str(context['object'].credito_da_imagem_principal)
        fonte_de_pesquisa = bs4.BeautifulSoup(str(context['object'].fonte_de_pesquisa), 'html.parser')
        if fonte_de_pesquisa.get_text('').strip():
            fonte_de_pesquisa = f'<div class="d3fontepesquisa">{fonte_de_pesquisa}</div>'
        else:
            fonte_de_pesquisa = ''
        fonte_e_credito = f'''
            <div class="d3credito">
            <div class="d3creditoimagemoed">{credito_imagem_prefixo} {credito_da_imagem_principal}</div>
            {fonte_de_pesquisa}
            </div>
            '''
        fonte_e_credito: str # capturar isso
        # CONCLUSÃO
        conclusao = str(context['object'].conclusao)
        conclusao = bs4.BeautifulSoup(conclusao, 'html.parser')
        if conclusao.get_text('').strip():
            conclusao = f'<div class="d3conclusaooed">{conclusao}</div>'
        else:
            conclusao = ''
        conclusao: str # capturar isso
        # COORDENADAS
        marcador_css: dict # capturar isso

        
        
        

except Exception as e:
    print(f"Erro ao testar: {e}")