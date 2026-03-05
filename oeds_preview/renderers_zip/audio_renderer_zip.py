from django.template.loader import render_to_string
import bs4
import io
import zipfile
import os
from django.http import HttpResponse


def zip_audio(context, template, oed):

    html_content = render_to_string(template, context)
    html_content = html_content.replace('/static/oeds_preview/', '../../')

    soup = bs4.BeautifulSoup(html_content, "lxml")

    # remove botões de interface
    for btn in soup.find_all(attrs={"class": "btn"}):
        btn.decompose()

    # ajustar caminho do áudio para funcionar localmente
    for source in soup.find_all("source"):
        if source.get("src"):
            source["src"] = os.path.basename(source["src"])

    html_content = str(soup)

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

        # XHTML
        zip_file.writestr(
            f"{oed.retranca}.xhtml",
            html_content
        )

        # MP3
        audio_path = oed.audio.arquivo_do_audio.path

        zip_file.write(
            audio_path,
            os.path.basename(audio_path)
        )

    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/zip")

    response["Content-Disposition"] = (
        f'attachment; filename="{oed.retranca}.zip"'
    )

    return response