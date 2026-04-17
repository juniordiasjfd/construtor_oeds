import bs4
import copy
import re
from PIL import Image
from django.utils.safestring import mark_safe
from oeds.models import TipoOed
from ..utils import renomeia_tags_and_apply_mathml


def render_pontos(oed):
    context = {}
    pontos = oed.pontos.all().order_by('id')
    
    # 1. TIPO + TITULO (Processamento com BeautifulSoup)
    soup_titulo = bs4.BeautifulSoup(f'<div class="d3tit1oed">{oed.titulo}</div>', 'html.parser')
    nivel_h = 2
    for p in soup_titulo.find_all(re.compile(r'^p$|h\d')):
        p.name = f'h{nivel_h}'
        nivel_h = (nivel_h + 1 if nivel_h <= 6 else nivel_h)
    
    soup_tipo = bs4.BeautifulSoup(str(oed.tipo), 'html.parser').p
    if soup_tipo:
        soup_tipo.name = 'span'
        soup_tipo['class'] = ['unwrap']
    soup_tipo = bs4.BeautifulSoup(f'<span class="d3titdestaque">{soup_tipo}:</span>', 'html.parser')
    soup_titulo.find('h2').insert(0, ' ')
    soup_titulo.find('h2').insert(0, copy.copy(soup_tipo))
    for un in soup_titulo.find_all(attrs={'class':'unwrap'}):
        un.unwrap()
    soup_titulo = renomeia_tags_and_apply_mathml(soup_titulo)
    context['html_titulo'] = mark_safe(str(soup_titulo))

    # 2. INSTRUÇÃO + PREFIXO CRÉDITO
    tipo_oed = TipoOed.objects.filter(pk=oed.tipo.pk).first()
    # context['tipo_oed'] = tipo_oed
    soup_instrucao = bs4.BeautifulSoup(tipo_oed.instrucao, 'html.parser')
    for p in soup_instrucao.find_all('p'):
        p['class'] = ['d3instrucaooed']
    soup_instrucao = renomeia_tags_and_apply_mathml(soup_instrucao)
    context['html_instrucao'] = mark_safe(f'<div>{soup_instrucao}</div>')
    
    # Prefixo de crédito (usado várias vezes)
    credito_imagem_prefixo = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(tipo_oed.credito_imagem_prefixo, 'html.parser').p)
    if credito_imagem_prefixo:
        credito_imagem_prefixo.name = 'span'

    # 3. INTRODUÇÃO
    soup_intro = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(str(oed.introducao), 'html.parser'))
    for p in soup_intro.find_all('p'):
        p['class'] = ['d3txtoed']
    if soup_intro.get_text(strip=True):
        context['html_introducao'] = mark_safe(f'<div class="d3txinstrucaooed">{soup_intro}</div>')
    else:
        context['html_introducao'] = ''

    # 4. IMAGEM PRINCIPAL (Redimensionamento dinâmico)
    if oed.imagem_principal:
        with Image.open(oed.imagem_principal.path) as img_p:
            new_width = 716
            new_height = round(img_p.height * (new_width / img_p.width))
        legenda_da_imagem_principal = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(f'<figcaption class="p4legenda">{oed.legenda_da_imagem_principal}</figcaption>', 'html.parser'))
        for p in legenda_da_imagem_principal.find_all('p'):
            p.name = 'span'
        context['img_principal_html'] = mark_safe(f'''
            <div class="img_info_enriquecimento">
            <figure>
                <!--Retranca original: {oed.retranca_da_imagem_principal}-->
                <img alt="{oed.alt_text_da_imagem_principal}" height="{new_height}" src="{oed.imagem_principal.url}" width="{new_width}" />
                {legenda_da_imagem_principal}
            </figure>
            </div>
            ''')

    # 5. PONTOS CLICÁVEIS (Loop e construção de lista)
    pontos_renderizados = []
    marcador_css_desktop = {}
    marcador_css_mobile = {}
    
    for i, ponto in enumerate(pontos, 1):
        # Coordenadas para o CSS
        if ponto.coordenadas:
            temporario_desktop = ponto.coordenadas.split(',')
            temporario_mobile = ponto.coordenadas.split(',')

            temporario_desktop[1] = str(0.8643356643356643 * float(temporario_desktop[1]) + 3.361454545454545)
            temporario_mobile[1] = str(    (0.8643356643356643 * float(temporario_mobile[1]) + 3.361454545454545)    *    0.80066808526)
            marcador_css_desktop[f'marcador{i}'] = temporario_desktop
            marcador_css_mobile[f'marcador{i}'] = temporario_mobile
        else:
            marcador_css_desktop[f'marcador{i}'] = ['0','0']
            marcador_css_mobile[f'marcador{i}'] = ['0','0']
        
        # Título do ponto
        soup_pt_titulo = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(str(ponto.titulo_ponto), 'html.parser'))
        if soup_pt_titulo.p:
            soup_pt_titulo.p.insert(0, f'{i}. ')
        
        # Imagem do ponto
        nw_pt = 678
        if ponto.imagem_do_ponto:
            with Image.open(ponto.imagem_do_ponto.path) as img_pt:
                nh_pt = round(img_pt.height * (nw_pt / img_pt.width))
            legenda_da_imagem_do_ponto = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(f'<figcaption class="p4legenda">{ponto.legenda_da_imagem_do_ponto}</figcaption>', 'html.parser'))
            for p in legenda_da_imagem_do_ponto.find_all('p'):
                p.name = 'span'
            html_imagem_do_ponto = f'''
                <div class="col2c">
                    <figure>
                        <!--Retranca original: {ponto.retranca_da_imagem_do_ponto}-->
                        <img alt="{ponto.alt_text_da_imagem_do_ponto}" height="{nh_pt}" src="{ponto.imagem_do_ponto.url}" width="{nw_pt}" />
                        {legenda_da_imagem_do_ponto}
                    </figure>
                </div>
            '''
        else:
            html_imagem_do_ponto = ''
            
        # Construção do HTML do ponto (usando f-string para clareza)
        credito_da_imagem_do_ponto = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(f'<div>{ponto.credito_da_imagem_do_ponto}</div>', 'html.parser'))
        if credito_da_imagem_do_ponto.get_text('').strip() in ['', 'None']:
            credito_da_imagem_do_ponto = ''
        elif type(credito_da_imagem_do_ponto) == bs4.BeautifulSoup:
            if credito_da_imagem_do_ponto.p and 'crédito' not in credito_da_imagem_do_ponto.get_text(strip=True).lower():
                credito_da_imagem_do_ponto.p.insert(0, ' ')
                credito_da_imagem_do_ponto.p.insert(0, copy.copy(credito_imagem_prefixo))
            for p in credito_da_imagem_do_ponto.find_all('p'):
                p['class'] = ['d3creditoimagemoed']
        else:
            credito_da_imagem_do_ponto = ''
        texto_ponto = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(f'<div>{ponto.texto_ponto}</div>', 'html.parser'))
        for p in texto_ponto.find_all('p'):
            p['class'] = ['d3txtoedmapitem']
        if texto_ponto.get_text('').strip() == '':
            texto_ponto = ''
        html_ponto = f'''
        <div class="mapa-item mapa-item{i}">
            <a class="marcador marcador{i}" href="#marcador{i}" id="ponto{i}">{i}</a>
            <div class="mapa-popup" id="marcador{i}" role="group">
                <div class="popup-titulo">{soup_pt_titulo}</div>
                {html_imagem_do_ponto}
                {credito_da_imagem_do_ponto}
                {texto_ponto}
                <a href="#ponto{i}" class="btn">{tipo_oed.botao_fechar}</a>
            </div>
        </div>'''
        pontos_renderizados.append(mark_safe(html_ponto))

    context['pontos_html'] = mark_safe('\n'.join(pontos_renderizados))
    context['marcador_css_desktop'] = marcador_css_desktop
    context['marcador_css_mobile'] = marcador_css_mobile

    # 6. FONTE E CRÉDITOS FINAIS
    fonte_soup = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(str(oed.fonte_de_pesquisa), 'html.parser'))
    for p in fonte_soup.find_all('p'):
        p['class'] = ['d3fontepesquisa']
    fonte_html = f'<div class="d3fontepesquisa">{fonte_soup}</div>' if fonte_soup.get_text(strip=True) else ''
    credito_da_imagem_principal = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(f'<div>{oed.credito_da_imagem_principal}</div>', 'html.parser'))
    if credito_da_imagem_principal.get_text('').strip() in ['', 'None']:
        credito_da_imagem_principal = ''
    elif type(credito_da_imagem_principal) == bs4.BeautifulSoup:
        if credito_da_imagem_principal.p and 'crédito' not in credito_da_imagem_principal.get_text(strip=True).lower():
            credito_da_imagem_principal.p.insert(0, ' ')
            credito_da_imagem_principal.p.insert(0, copy.copy(credito_imagem_prefixo))
        for p in credito_da_imagem_principal.find_all('p'):
            p['class'] = ['d3creditoimagemoed']
    else:
        credito_da_imagem_principal = ''


    context['html_fonte_e_credito'] = mark_safe(f'''
        <div class="d3credito">
            {credito_da_imagem_principal}
            {fonte_html}
        </div>''')

    # 7. CONCLUSÃO
    concl_soup = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(str(oed.conclusao), 'html.parser'))
    for p in concl_soup.find_all('p'):
        p['class'] = ['d3txtoed']
    context['html_conclusao'] = mark_safe(f'<div class="d3conclusaooed">{concl_soup}</div>') if concl_soup.get_text(strip=True) else ''

    return context