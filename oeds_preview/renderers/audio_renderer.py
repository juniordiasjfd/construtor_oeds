import bs4
from django.utils.safestring import mark_safe
from ..utils import renomeia_tags_and_apply_mathml


def render_audio(oed):

    context = {}

    audio = oed.audio

    context["audio_src"] = audio.arquivo_do_audio.url

    # título
    context["html_titulo"] = oed.titulo

    # transcrição
    soup_transcricao = renomeia_tags_and_apply_mathml(
        bs4.BeautifulSoup(str(audio.transcricao_do_audio), "html.parser")
    )

    for p in soup_transcricao.find_all("p"):
        p["class"] = ["d3txtoed"]

    context["html_transcricao"] = mark_safe(str(soup_transcricao))

    # créditos
    soup_creditos = renomeia_tags_and_apply_mathml(
        bs4.BeautifulSoup(str(audio.creditos_do_audio), "html.parser")
    )

    for p in soup_creditos.find_all("p"):
        p["class"] = ["d3creditoimagemoed"]

    context["html_creditos_audio"] = mark_safe(str(soup_creditos))

    return context