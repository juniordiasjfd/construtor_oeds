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
    soup_titulo = bs4.BeautifulSoup(f'<div class="d3tit1oed">{oed.titulo}</div>', 'html.parser')
    print(soup_titulo)
    nivel_h = 1
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

    # css adicional
    context['css_adicional'] = mark_safe('''
    <style>
    .c3idiomabold{font-style:italic;font-weight:bold}.c3idiomaitalico{font-style:italic}.c3idiomabolditalico{font-style:italic;font-weight:bold}.url_para_encurtar{background-color: lightgreen}
    .borda_interna {padding: 10px !important;}
    .d3txtranscanto{
        font-style: italic;
        margin:0.5em 0 0.5em  0;
        }
        .d3rubricatxad{
        font-weight: bold;
        margin: 1em 0 0.4em 0;
        }
        .d3rubricatranscricao {
        font-weight: bold;
                                         }
        .d3vinhetaabertura {
        margin:1em 0 0  0;
        font-style: italic;
        }

        .d3txad{
        margin: 0.5em 0;
        font-family: var(--texto);}

        .d3creditosoed {
        margin: 1em 0 0 0;
        }



        .d3txtranscanto{
        font-style: italic;
        margin:0.5em 0 0.5em  0;
        }
        .d3rubricatxad{
        font-weight: bold;
        margin: 1em 0 0.4em 0;
        }
        .d3vinheta {
        margin:1em 0 0  0;
        font-style: italic;
        }

        .d3txad{
        margin: 0.5em 0;
        font-family: var(--texto);}

        .d3creditosoed {
        margin: 1em 0 0 0;
        }
                                         /* Botões de download no preview */
body > a.btn {
    display: inline-block;
    font-family: var(--texto);
    font-size: var(--pesoIntermediario);
    text-decoration: none;
    padding: 0.45em 1em;
    margin: 0.8em 0.4em 1em 0;
    border-radius: 6px;
    border: 1px solid var(--azul1b);
    transition: all 0.2s ease-in-out;
}

/* botão principal (ZIP) */
body > a.btn-primary {
    background: var(--azul1);
    color: var(--branco);
}

body > a.btn-primary:hover {
    background: var(--azul1b);
    border-color: var(--azul1b);
}

/* botão secundário (PDF) */
body > a.btn-secondary {
    background: transparent;
    color: var(--azul1b);
}

body > a.btn-secondary:hover {
    background: var(--azul2);
}

    </style>
    ''')

    return context