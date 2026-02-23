from django.views.generic import DetailView
from oeds.models import Oed, TipoOed
import bs4
from PIL import Image
from django.utils.safestring import mark_safe
import copy
import io
import zipfile
import os
import re
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View
import datetime
from usuarios.views import ComumInternoRequiredMixin
from .latex import html_with_latex_class_2_html_with_mathml
from xhtml2pdf import pisa


def has_parent_with(tag:bs4.element.Tag, parent_name='em'):
    parents_names = list(x.name for x in tag.parents)
    return parent_name in parents_names
def renomeia_tags_and_apply_mathml(
        soup:bs4.BeautifulSoup, 
        de_para={
            'i':'em', 
            'b':'strong'
            }):
    for old_name in de_para:
        ocorrencias = soup.find_all(old_name)
        for ocor in ocorrencias:
            ocor.name = de_para[old_name]
    ocorrencias = soup.find_all('strong')
    for ocor in ocorrencias:
        if has_parent_with(ocor, 'em'):
            new_em = soup.new_tag('em')
            ocor.insert_before(new_em)
            new_em.append(ocor)
            new_em.name = 'strong'
            ocor.name = 'em'
    soup = html_with_latex_class_2_html_with_mathml(soup)
    return soup
class OedPreviewDetailView(DetailView):
    model = Oed
    template_name = 'oeds_preview/preview.xhtml' # O caminho do seu template específico
    context_object_name = 'oed'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        pontos = obj.pontos.all().order_by('id')
        
        # 1. TIPO + TITULO (Processamento com BeautifulSoup)
        soup_titulo = bs4.BeautifulSoup(f'<div class="d3tit1oed">{obj.titulo}</div>', 'html.parser')
        nivel_h = 1
        for p in soup_titulo.find_all(re.compile(r'^p$|h\d')):
            p.name = f'h{nivel_h}'
            nivel_h = (nivel_h + 1 if nivel_h <= 6 else nivel_h)
        
        soup_tipo = bs4.BeautifulSoup(str(obj.tipo), 'html.parser').p
        if soup_tipo:
            soup_tipo.name = 'span'
            soup_tipo['class'] = ['unwrap']
        soup_tipo = bs4.BeautifulSoup(f'<span class="d3titdestaque">{soup_tipo}:</span>', 'html.parser')
        soup_titulo.find('h1').insert(0, ' ')
        soup_titulo.find('h1').insert(0, copy.copy(soup_tipo))
        for un in soup_titulo.find_all(attrs={'class':'unwrap'}):
            un.unwrap()
        soup_titulo = renomeia_tags_and_apply_mathml(soup_titulo)
        context['html_titulo'] = mark_safe(str(soup_titulo))

        # 2. INSTRUÇÃO + PREFIXO CRÉDITO
        tipo_oed = TipoOed.objects.filter(pk=obj.tipo.pk).first()
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
        soup_intro = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(str(obj.introducao), 'html.parser'))
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
            legenda_da_imagem_principal = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(f'<figcaption class="p4legenda">{obj.legenda_da_imagem_principal}</figcaption>', 'html.parser'))
            for p in legenda_da_imagem_principal.find_all('p'):
                p.name = 'span'
            context['img_principal_html'] = mark_safe(f'''
                <div class="img_info_enriquecimento">
                <figure>
                    <!--Retranca original: {obj.retranca_da_imagem_principal}-->
                    <img alt="{obj.alt_text_da_imagem_principal}" height="{new_height}" src="{obj.imagem_principal.url}" width="{new_width}" />
                    <figcaption>{legenda_da_imagem_principal}</figcaption>
                </figure>
                </div>
                ''')

        # 5. PONTOS CLICÁVEIS (Loop e construção de lista)
        pontos_renderizados = []
        marcador_css = {}
        
        for i, ponto in enumerate(pontos, 1):
            # Coordenadas para o CSS
            if ponto.coordenadas:
                temporario = ponto.coordenadas.split(',')
                temporario[1] = str(0.8643356643356643 * float(temporario[1]) + 3.361454545454545)
                marcador_css[f'marcador{i}'] = temporario
            else:
                marcador_css[f'marcador{i}'] = ['0','0']
            
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
        context['marcador_css'] = marcador_css

        # 6. FONTE E CRÉDITOS FINAIS
        fonte_soup = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(str(obj.fonte_de_pesquisa), 'html.parser'))
        for p in fonte_soup.find_all('p'):
            p['class'] = ['d3fontepesquisa']
        fonte_html = f'<div class="d3fontepesquisa">{fonte_soup}</div>' if fonte_soup.get_text(strip=True) else ''
        credito_da_imagem_principal = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(f'<div>{obj.credito_da_imagem_principal}</div>', 'html.parser'))
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
        concl_soup = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(str(obj.conclusao), 'html.parser'))
        for p in concl_soup.find_all('p'):
            p['class'] = ['d3txtoed']
        context['html_conclusao'] = mark_safe(f'<div class="d3conclusaooed">{concl_soup}</div>') if concl_soup.get_text(strip=True) else ''

        return context
class OedDownloadZipView(ComumInternoRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # 1. Obter o objeto e os dados do contexto
        # Dica: Reutilize a lógica da sua OedPreviewDetailView
        preview_view = OedPreviewDetailView()
        preview_view.object = Oed.objects.get(pk=self.kwargs['pk'])
        context = preview_view.get_context_data(object=preview_view.object)
        
        # 2. Renderizar o HTML
        html_content = render_to_string('oeds_preview/preview.xhtml', context)
        html_content = html_content.replace('/static/oeds_preview/', '')
        html_content = html_content.replace('/media/oeds/', '')
        soup = bs4.BeautifulSoup(html_content, 'lxml')
        # retirada do botão
        botao_zip = soup.find(attrs={'class':'btn-primary'})
        if botao_zip:
            botao_zip.decompose()
        botao_pdf = soup.find(attrs={'class':'btn-secondary'})
        if botao_pdf:
            botao_pdf.decompose()
        # filtrando as imagens
        lista_de_imagens = list(os.path.basename(x['href']) for x in soup.find_all(attrs={'href':True}))
        lista_de_imagens += list(os.path.basename(x['src']) for x in soup.find_all(attrs={'src':True}))
        html_content = str(soup)

        # 3. Criar o arquivo ZIP em memória
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            # Adicionar o arquivo HTML principal
            zip_file.writestr(f'{preview_view.object.retranca}.xhtml', html_content)

            # 4. Adicionar Arquivos Estáticos (Styles, Fonts, Images do Static)
            # Define os caminhos das pastas dentro do seu app oeds_preview
            static_root = os.path.join(settings.BASE_DIR, 'oeds_preview', 'static', 'oeds_preview')
            
            folders_to_include = ['styles', 'fonts', 'images']
            
            for folder in folders_to_include:
                folder_path = os.path.join(static_root, folder)
                if os.path.exists(folder_path):
                    for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            file_full_path = os.path.join(root, file)
                            # Cria o caminho relativo dentro do ZIP (ex: styles/arquivo.css)
                            rel_path = os.path.relpath(file_full_path, static_root)
                            if folder == 'images':
                                if os.path.basename(rel_path) not in lista_de_imagens:
                                    continue
                            zip_file.write(file_full_path, rel_path)

            # 5. Adicionar Imagens de Media (Uploads do Banco de Dados)
            # Aqui você deve decidir se quer manter a estrutura original ou mover para images/
            obj = preview_view.object
            if obj.imagem_principal:
                zip_file.write(obj.imagem_principal.path, f"images/{os.path.basename(obj.imagem_principal.path)}")
            
            for ponto in obj.pontos.all():
                if ponto.imagem_do_ponto:
                    zip_file.write(ponto.imagem_do_ponto.path, f"images/{os.path.basename(ponto.imagem_do_ponto.path)}")

        # 6. Retornar o ZIP como resposta de download
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/zip')
        hora = format(datetime.datetime.now(), '%Y-%m-%d_%H-%M-%S')
        response['Content-Disposition'] = f'attachment; filename="{preview_view.object.retranca}_export_{hora}.zip"'
        return response

class OedDownloadPDFView(ComumInternoRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # 1. Obter o objeto e os dados do contexto (Reutilizando sua lógica existente)
        preview_view = OedPreviewDetailView()
        preview_view.object = Oed.objects.get(pk=self.kwargs['pk'])
        context = preview_view.get_context_data(object=preview_view.object)
        
        # 2. Renderizar o HTML e limpar com BeautifulSoup
        html_string = render_to_string('oeds_preview/preview.xhtml', context)
        soup = bs4.BeautifulSoup(html_string, 'lxml')
        for fig in soup.find_all('figcaption'):
            fig.name = 'p'

        # Remove CSS e Scripts originais para o PDF ficar limpo
        for s in soup.find_all(['link', 'style', 'script']):
            s.decompose()
        
        # Remove botões de interface
        for btn in soup.find_all(attrs={'class': 'btn'}):
            btn.decompose()

        # Ajuste de caminhos de imagem para o xhtml2pdf encontrar os arquivos no servidor
        for img in soup.find_all('img'):
            if img.get('src') and img['src'].startswith('/media/'):
                # Transforma a URL do browser em caminho de arquivo local
                relative_path = img['src'].replace('/media/', '')
                img['src'] = os.path.join(settings.MEDIA_ROOT, relative_path)

        # 3. Adicionar estilo básico para impressão
        estilo_pdf = soup.new_tag('style')
        estilo_pdf.string = """
            @page { size: a4 portrait; margin: 1cm; }
            body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.4; }
            h1, h2, h3 { color: #333; margin-top: 15pt; }
            img { max-width: 100%; height: auto; }
            .mapa-popup { border: 0.5pt solid #aaa; padding: 10px; margin-bottom: 20px; }
        """
        soup.head.append(estilo_pdf)

        # 4. Gerar o PDF
        html_final = str(soup)
        result = io.BytesIO()
        
        # O pisa.pisaDocument transforma o HTML em PDF
        pdf = pisa.pisaDocument(io.BytesIO(html_final.encode("utf-8")), result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            hora = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"{preview_view.object.retranca}_{hora}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        return HttpResponse("Erro técnico ao gerar o PDF.", status=500)