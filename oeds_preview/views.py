from django.views.generic import DetailView
from oeds.models import Oed, TipoOed
import bs4
from PIL import Image
from django.utils.safestring import mark_safe
import copy


class OedPreviewDetailView(DetailView):
    model = Oed
    template_name = 'oeds_preview/preview.xhtml' # O caminho do seu template específico
    context_object_name = 'oed'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        pontos = obj.pontos.all().order_by('id')
        
        # 1. TIPO + TITULO (Processamento com BeautifulSoup)
        soup_tipo = bs4.BeautifulSoup(str(obj.tipo), 'html.parser').p
        if soup_tipo:
            soup_tipo.name = 'span'
            soup_tipo['class'] = ['unwrap']
            
        html_titulo = f'<div class="d3tit1oed">{obj.titulo}</div>'
        soup_titulo = bs4.BeautifulSoup(html_titulo, 'html.parser')
        nivel_h = 1
        for p in soup_titulo.find_all('p'):
            p.name = f'h{nivel_h}'
            nivel_h = (nivel_h + 1 if nivel_h <= 6 else nivel_h)
        
        soup_tipo = bs4.BeautifulSoup(f'<span class="d3titdestaque">{soup_tipo}:</span>', 'html.parser')
        soup_titulo.find('h1').insert(0, ' ')
        soup_titulo.find('h1').insert(0, soup_tipo)
        for un in soup_titulo.find_all(attrs={'class':'unwrap'}):
            un.unwrap()

        context['html_titulo'] = mark_safe(str(soup_titulo))

        # 2. INSTRUÇÃO + PREFIXO CRÉDITO
        tipo_oed = TipoOed.objects.filter(pk=obj.tipo.pk).first()
        context['tipo_oed'] = tipo_oed
        soup_instrucao = bs4.BeautifulSoup(tipo_oed.instrucao, 'html.parser')
        for p in soup_instrucao.find_all('p'):
            p['class'] = ['d3instrucaooed']
        context['html_instrucao'] = mark_safe(f'<div class="d3instrucaooed">{soup_instrucao}</div>')
        
        # Prefixo de crédito (usado várias vezes)
        credito_imagem_prefixo = bs4.BeautifulSoup(tipo_oed.credito_imagem_prefixo, 'html.parser').p
        if credito_imagem_prefixo:
            credito_imagem_prefixo.name = 'span'

        # 3. INTRODUÇÃO
        soup_intro = bs4.BeautifulSoup(str(obj.introducao), 'html.parser')
        for p in soup_intro.find_all('p'):
            p['class'] = ['d3txtoed']
        if soup_intro.get_text(strip=True):
            context['html_introducao'] = mark_safe(f'<div class="d3txinstrucaooed">{soup_intro}</div>')
        else:
            context['html_introducao'] = ''

        # 4. IMAGEM PRINCIPAL (Redimensionamento dinâmico)
        if obj.imagem_principal:
            with Image.open(obj.imagem_principal.path) as img_p:
                new_width = 716
                new_height = round(img_p.height * (new_width / img_p.width))
                context['img_principal_html'] = mark_safe(
                    f'<img alt="{obj.alt_text_da_imagem_principal}" height="{new_height}" '
                    f'src="{obj.imagem_principal.url}" width="{new_width}"/>'
                )
            
            context['html_legenda_principal'] = mark_safe(
                f'<div class="p4legenda">{obj.legenda_da_imagem_principal}</div>'
            )

        # 5. PONTOS CLICÁVEIS (Loop e construção de lista)
        pontos_renderizados = []
        marcador_css = {}
        
        for i, ponto in enumerate(pontos, 1):
            # Coordenadas para o CSS
            marcador_css[f'marcador{i}'] = ponto.coordenadas.split(',')
            
            # Título do ponto
            soup_pt_titulo = bs4.BeautifulSoup(str(ponto.titulo_ponto), 'html.parser')
            if soup_pt_titulo.p:
                soup_pt_titulo.p.insert(0, f'{i}. ')
            
            # Imagem do ponto
            with Image.open(ponto.imagem_do_ponto.path) as img_pt:
                nw_pt = 678
                nh_pt = round(img_pt.height * (nw_pt / img_pt.width))
                
            # Construção do HTML do ponto (usando f-string para clareza)
            credito_da_imagem_do_ponto = bs4.BeautifulSoup(str(ponto.credito_da_imagem_do_ponto), 'html.parser')
            if credito_da_imagem_do_ponto.get_text('').strip() in ['', 'None']:
                credito_da_imagem_do_ponto = ''
            elif type(credito_da_imagem_do_ponto) == bs4.BeautifulSoup:
                if credito_da_imagem_do_ponto.p:
                    credito_da_imagem_do_ponto.p.insert(0, ' ')
                    credito_da_imagem_do_ponto.p.insert(0, copy.copy(credito_imagem_prefixo))
            else:
                credito_da_imagem_do_ponto = ''
            html_ponto = f'''
            <div class="mapa-item mapa-item{i}">
                <a class="marcador marcador{i}" href="#marcador{i}" id="ponto{i}">{i}</a>
                <div class="mapa-popup" id="marcador{i}" role="group">
                    <div class="popup-titulo">{soup_pt_titulo}</div>
                    <div class="col2c">
                        <figure>
                            <img alt="{ponto.alt_text_da_imagem_do_ponto}" height="{nh_pt}" src="{ponto.imagem_do_ponto.url}" width="{nw_pt}" />
                            <figcaption class="p4legenda">{ponto.legenda_da_imagem_do_ponto}</figcaption>
                        </figure>
                    </div>
                    <div class="d3creditoimagemoed">{credito_da_imagem_do_ponto}</div>
                    <div class="d3txtoedmapitem">{ponto.texto_ponto}</div>
                    <a href="#ponto{i}" class="btn">{tipo_oed.botao_fechar}</a>
                </div>
            </div>'''
            pontos_renderizados.append(mark_safe(html_ponto))

        context['pontos_html'] = mark_safe('\n'.join(pontos_renderizados))
        context['marcador_css'] = marcador_css

        # 6. FONTE E CRÉDITOS FINAIS
        fonte_soup = bs4.BeautifulSoup(str(obj.fonte_de_pesquisa), 'html.parser')
        fonte_html = f'<div class="d3fontepesquisa">{fonte_soup}</div>' if fonte_soup.get_text(strip=True) else ''
        credito_da_imagem_principal = bs4.BeautifulSoup(str(obj.credito_da_imagem_principal), 'html.parser')
        if credito_da_imagem_principal.get_text('').strip() in ['', 'None']:
            credito_da_imagem_principal = ''
        elif type(credito_da_imagem_principal) == bs4.BeautifulSoup:
            if credito_da_imagem_principal.p:
                credito_da_imagem_principal.p.insert(0, ' ')
                credito_da_imagem_principal.p.insert(0, copy.copy(credito_imagem_prefixo))
        else:
            credito_da_imagem_principal = ''


        context['html_fonte_e_credito'] = mark_safe(f'''
            <div class="d3credito">
                <div class="d3creditoimagemoed">{credito_da_imagem_principal}</div>
                {fonte_html}
            </div>''')

        # 7. CONCLUSÃO
        concl_soup = bs4.BeautifulSoup(str(obj.conclusao), 'html.parser')
        for p in concl_soup.find_all('p'):
            p['class'] = ['d3txtoed']
        context['html_conclusao'] = mark_safe(f'<div class="d3conclusaooed">{concl_soup}</div>') if concl_soup.get_text(strip=True) else ''

        return context

