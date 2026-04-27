import bs4
from django.utils.safestring import mark_safe
from ..utils import renomeia_tags_and_apply_mathml
import re
import copy
from oeds.models import TipoOed


def render_audio(oed):

    context = {}

    print(oed.titulo)

    # 1. TIPO + TITULO (Processamento com BeautifulSoup)
    soup_tipo = bs4.BeautifulSoup(str(oed.tipo), 'html.parser')
    for p in soup_tipo.find_all(re.compile(r'^p$|h\d')):
        p.name = 'span'
    soup_tit = bs4.BeautifulSoup(str(oed.titulo), 'html.parser')
    for p in soup_tit.find_all(re.compile(r'^p$|h\d')):
        p.name = 'span'
    soup_titulo = bs4.BeautifulSoup(f'<div class="d3tit1oed"><h2>{soup_tipo}: {soup_tit}</h2></div>', 'html.parser')
    print(soup_titulo)
    nivel_h = 2
    for p in soup_titulo.find_all(re.compile(r'^p$|h\d')):
        p.name = f'h{nivel_h}'
        nivel_h = (nivel_h + 1 if nivel_h <= 6 else nivel_h)
    
    soup_titulo = renomeia_tags_and_apply_mathml(soup_titulo)
    context['html_titulo'] = mark_safe(str(soup_titulo))



    # 2. INSTRUÇÃO
    tipo_oed = TipoOed.objects.filter(pk=oed.tipo.pk).first()
    soup_instrucao = bs4.BeautifulSoup(tipo_oed.instrucao, 'html.parser')
    for p in soup_instrucao.find_all('p'):
        p['class'] = ['d3instrucaooed']
    soup_instrucao = renomeia_tags_and_apply_mathml(soup_instrucao)
    context['html_instrucao'] = mark_safe(f'<div>{soup_instrucao}</div>')




    # 2.5 TEXTO INTRODUÇÃO, CONCLUSÃO E FONTE DE PESQUISA
    soup_intro = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(str(oed.introducao), 'html.parser'))
    for p in soup_intro.find_all('p'):
        p['class'] = ['d3txtoed']
    context['html_introducao'] = mark_safe(f'<div class="d3txinstrucaooed">{soup_intro}</div>') if soup_intro.get_text(strip=True) not in ['', 'None'] else ''
    

    fonte_soup = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(str(oed.fonte_de_pesquisa), 'html.parser'))
    for p in fonte_soup.find_all('p'):
        p['class'] = ['d3fontepesquisa']
    fonte_html = f'<div class="d3fontepesquisa">{fonte_soup}</div>' if fonte_soup.get_text(strip=True) not in ['', 'None'] else ''
    context['fonte_html'] = mark_safe(fonte_html)

    concl_soup = renomeia_tags_and_apply_mathml(bs4.BeautifulSoup(str(oed.conclusao), 'html.parser'))
    for p in concl_soup.find_all('p'):
        p['class'] = ['d3txtoed']
    context['html_conclusao'] = mark_safe(f'<div class="d3conclusaooed">{concl_soup}</div>') if concl_soup.get_text(strip=True) not in ['', 'None'] else ''



    # 3. ARQUIVO DO ÁUDIO
    audio = oed.audio
    if audio.arquivo_do_audio:
        context["audio_src"] = audio.arquivo_do_audio.url
    else:
        context["audio_src"] = 'audio.mp3'



    # 4. transcrição
    soup_transcricao = renomeia_tags_and_apply_mathml(
        bs4.BeautifulSoup(str(audio.transcricao_do_audio), "html.parser")
    )
    context["html_transcricao"] = mark_safe(str(soup_transcricao))



    # créditos
    soup_creditos = renomeia_tags_and_apply_mathml(
        bs4.BeautifulSoup(str(audio.creditos_do_audio), "html.parser")
    )
    context["html_creditos_audio"] = mark_safe(str(soup_creditos))

    return context